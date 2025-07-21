
# desktop_app.py

import asyncio
import logging
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import json
from torrentnode import Node, NodeConfig
from torrentnode.task_executor import Task, TaskType # Прямой импорт
import time # Added for time formatting in chat


# --- GUI Log Handler ---
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

# --- Main Application ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TorrentNode Net")
        self.geometry("900x700")

        self.node = None
        self.node_thread = None
        self.loop = None
        
        # --- Main Layout ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Left Column ---
        left_column = ttk.Frame(main_frame)
        left_column.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        
        # --- Right Column for Tabs (Logs and Chat) ---
        right_column = ttk.Frame(main_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Tab Control ---
        self.notebook = ttk.Notebook(right_column)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # --- Log Viewer Tab ---
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Logs")
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # --- Network Peers Tab ---
        peers_frame = ttk.Frame(self.notebook)
        self.notebook.add(peers_frame, text="Network Peers (0)")
        
        self.peers_tree = ttk.Treeview(peers_frame, columns=('id', 'address'), show='headings')
        self.peers_tree.heading('id', text='Peer ID')
        self.peers_tree.heading('address', text='Address')
        self.peers_tree.column('id', width=200)
        self.peers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Chat Tab ---
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="Global Chat")
        
        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        chat_input_frame = ttk.Frame(chat_frame)
        chat_input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.chat_entry = ttk.Entry(chat_input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_entry.bind("<Return>", self.send_chat_message)
        
        self.send_chat_button = ttk.Button(chat_input_frame, text="Send", command=self.send_chat_message)
        self.send_chat_button.pack(side=tk.RIGHT, padx=(5,0))


        # --- Control Panel ---
        controls_frame = ttk.Labelframe(left_column, text="Control Panel")
        controls_frame.pack(pady=5, fill=tk.X)

        self.start_button = ttk.Button(controls_frame, text="Start Node", command=self.start_node)
        self.start_button.pack(pady=10, padx=10, fill=tk.X)

        self.stop_button = ttk.Button(controls_frame, text="Stop Node", command=self.stop_node, state=tk.DISABLED)
        self.stop_button.pack(pady=5, padx=10, fill=tk.X)
        
        # --- Status Panel ---
        status_frame = ttk.Labelframe(left_column, text="Node Status")
        status_frame.pack(pady=10, fill=tk.X)

        self.status_label = ttk.Label(status_frame, text="Status: Stopped", foreground="red")
        self.status_label.pack(pady=5, padx=10, anchor=tk.W)

        self.status_vars = {
            "Node ID": tk.StringVar(value="N/A"),
            "Listening Port": tk.StringVar(value="N/A"),
            "DHT Nodes": tk.StringVar(value="N/A"),
            "Peers": tk.StringVar(value="N/A"),
        }
        
        bold_font = font.Font(weight="bold")
        for name, var in self.status_vars.items():
            f = ttk.Frame(status_frame)
            f.pack(fill=tk.X, padx=10, pady=2)
            ttk.Label(f, text=f"{name}:", font=bold_font).pack(side=tk.LEFT)
            ttk.Label(f, textvariable=var, wraplength=180, justify=tk.LEFT).pack(side=tk.LEFT, padx=(5,0))

        self.balance_button = ttk.Button(status_frame, text="Get Balance", command=self.get_balance, state=tk.DISABLED)
        self.balance_button.pack(pady=10, padx=10, fill=tk.X)

        # --- Task Creation ---
        task_frame = ttk.Labelframe(left_column, text="Create Task")
        task_frame.pack(pady=5, fill=tk.X)

        ttk.Label(task_frame, text="Task Type:").pack(padx=10, pady=(10,0), anchor=tk.W)
        self.task_type_entry = ttk.Entry(task_frame)
        self.task_type_entry.pack(pady=5, padx=10, fill=tk.X)
        self.task_type_entry.insert(0, "SUM")

        ttk.Label(task_frame, text="Data (JSON list):").pack(padx=10, pady=0, anchor=tk.W)
        self.task_data_entry = ttk.Entry(task_frame)
        self.task_data_entry.pack(pady=5, padx=10, fill=tk.X)
        self.task_data_entry.insert(0, "[1, 2, 3]")
        
        ttk.Label(task_frame, text="Reward:").pack(padx=10, pady=0, anchor=tk.W)
        self.task_reward_entry = ttk.Entry(task_frame)
        self.task_reward_entry.pack(pady=5, padx=10, fill=tk.X)
        self.task_reward_entry.insert(0, "10")

        self.create_task_button = ttk.Button(task_frame, text="Submit Task", command=self.create_task, state=tk.DISABLED)
        self.create_task_button.pack(pady=10, padx=10, fill=tk.X)

        # --- Setup logging ---
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.queue_handler)
        logging.getLogger().setLevel(logging.INFO)

        self.after(100, self.poll_log_queue)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message, level="info"):
        logger = logging.getLogger("GUI")
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)

    def poll_log_queue(self):
        # Process logs
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.log_area.configure(state=tk.NORMAL)
                self.log_area.insert(tk.END, record + '\n')
                self.log_area.configure(state=tk.DISABLED)
                self.log_area.see(tk.END)
        
        # Process chat messages
        if self.node:
            while not self.node.chat_queue.empty():
                try:
                    msg = self.node.chat_queue.get_nowait()
                    self.display_chat_message(msg)
                except queue.Empty:
                    break

        self.after(100, self.poll_log_queue)
    
    def display_chat_message(self, msg_data):
        try:
            author = msg_data.get(b'author', b'Unknown').decode('utf-8', 'replace')
            text = msg_data.get(b'text', b'').decode('utf-8', 'replace')
            ts = int(msg_data.get(b'ts', 0))
            
            # Simple time formatting
            msg_time = time.strftime('%H:%M:%S', time.localtime(ts))
            
            self.chat_area.configure(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"[{msg_time}] {author}: {text}\n")
            self.chat_area.configure(state=tk.DISABLED)
            self.chat_area.see(tk.END)
        except Exception as e:
            self.log(f"Failed to display chat message: {e}", "error")

    def send_chat_message(self, event=None):
        text = self.chat_entry.get()
        if text and self.node:
            # For now, use a simple author name. Later this can be a user-defined nickname.
            author_name = f"Node-{self.node.node_id[:6]}"
            asyncio.run_coroutine_threadsafe(self.node.send_chat_message(author_name, text), self.loop)
            self.chat_entry.delete(0, tk.END)

    def update_status_display(self, status_data):
        self.status_vars["Node ID"].set(status_data.get("node_id", "N/A"))
        self.status_vars["Listening Port"].set(status_data.get("listening_port", "N/A"))
        self.status_vars["DHT Nodes"].set(status_data.get("dht_nodes", "N/A"))
        self.status_vars["Peers"].set(status_data.get("num_peers", "N/A"))
        
        status_text = status_data.get("status", "stopped")
        if status_text == "running":
            self.status_label.config(text="Status: Running", foreground="green")
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
        
        # Update peers tab
        peers_list = status_data.get("peers", [])
        self.notebook.tab(1, text=f"Network Peers ({len(peers_list)})") # Update tab title with count
        
        # Efficiently update Treeview
        current_peers = {self.peers_tree.item(i)['values'][0] for i in self.peers_tree.get_children()}
        new_peers_map = {p['id']: (p['id'], p['address']) for p in peers_list}
        
        to_add = set(new_peers_map.keys()) - current_peers
        to_remove = current_peers - set(new_peers_map.keys())
        
        for peer_id in to_remove:
            for item in self.peers_tree.get_children():
                if self.peers_tree.item(item)['values'][0] == peer_id:
                    self.peers_tree.delete(item)
                    break
        
        for peer_id in to_add:
            self.peers_tree.insert('', 'end', values=new_peers_map[peer_id])


    def start_node(self):
        self.log("Starting node...")
        
        self.loop = asyncio.new_event_loop()
        # Конфигурация теперь использует значения по умолчанию
        config = NodeConfig(port=8888, data_dir="node_data", torrent_dir="node_torrents")
        self.node = Node(config=config, loop=self.loop)

        self.node_thread = threading.Thread(target=self.run_node_in_thread, daemon=True)
        self.node_thread.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.balance_button.config(state=tk.NORMAL)
        self.create_task_button.config(state=tk.NORMAL)
        
        self.after(1000, self.periodic_status_check)

    def run_node_in_thread(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.node.start())
        except Exception as e:
            # Логируем ошибку, если она произошла в самом потоке
            self.log(f"Node thread error: {e}", level="error")
        finally:
            self.loop.close()
            self.log("Event loop closed.", "info")


    def stop_node(self):
        self.log("Stopping node...")
        if self.node and self.node.running and self.loop.is_running():
            # Запускаем `stop` в цикле событий и ждем завершения
            future = asyncio.run_coroutine_threadsafe(self.node.stop(), self.loop)
            try:
                # Даем время на корректную остановку
                future.result(timeout=10)
            except Exception as e:
                 self.log(f"Error during node stop: {e}", level="error")
        
        # Поток должен завершиться сам после остановки цикла
        if self.node_thread and self.node_thread.is_alive():
            self.node_thread.join(timeout=5)

        self.node = None
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.balance_button.config(state=tk.DISABLED)
        self.create_task_button.config(state=tk.DISABLED)
        
        self.update_status_display({"status": "stopped"}) # Reset status display
        
        # Clear peers tab on disconnect
        for i in self.peers_tree.get_children():
            self.peers_tree.delete(i)
        self.notebook.tab(1, text="Network Peers (0)")

        # Clear chat window on disconnect
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.insert(tk.END, "Disconnected. Start node to join chat.\n")
        self.chat_area.configure(state=tk.DISABLED)
        self.log("Node stopped.")
    
    def periodic_status_check(self):
        if self.node:
            status = self.node.get_status()
            self.update_status_display(status)
            self.after(2000, self.periodic_status_check) # Schedule next check


    def get_balance(self):
        if self.node and self.loop:
            future = asyncio.run_coroutine_threadsafe(self.node.get_balance(), self.loop)
            try:
                balance = future.result(timeout=5)
                messagebox.showinfo("Balance", f"Your current balance is: {balance:.2f} TNT")
            except Exception as e:
                self.log(f"Error getting balance: {e}", level="error")
                messagebox.showerror("Error", f"Could not retrieve balance: {e}")

    def create_task(self):
        task_type_str = self.task_type_entry.get().upper()
        data_str = self.task_data_entry.get()
        reward_str = self.task_reward_entry.get()
        
        if not all([task_type_str, data_str, reward_str]):
            messagebox.showerror("Error", "All task fields are required.")
            return
            
        try:
            task_type = TaskType[task_type_str]
        except KeyError:
            messagebox.showerror("Error", f"Invalid task type: {task_type_str}. Available: {', '.join(TaskType.__members__)}")
            return

        try:
            # Преобразуем данные из строки JSON
            data = json.loads(data_str)
        except json.JSONDecodeError:
             messagebox.showerror("Error", "Data must be a valid JSON list or object.")
             return

        try:
            reward_val = float(reward_str)
        except ValueError:
            messagebox.showerror("Error", "Reward must be a number.")
            return

        # Создаем экземпляр Task
        task = Task(type=task_type, data=data, reward=reward_val)

        if self.node and self.loop:
            future = asyncio.run_coroutine_threadsafe(self.node.distribute_task(task), self.loop)
            try:
                task_id = future.result(timeout=10)
                self.log(f"Submitted task successfully. Task ID: {task_id}")
                messagebox.showinfo("Success", f"Task submitted with ID: {task_id}")
            except Exception as e:
                self.log(f"Error submitting task: {e}", level="error")
                messagebox.showerror("Error", f"Could not submit task: {e}")

    def on_closing(self):
        if self.node:
            if messagebox.askokcancel("Quit", "Node is running. Do you want to stop it and quit?"):
                self.stop_node()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop() 