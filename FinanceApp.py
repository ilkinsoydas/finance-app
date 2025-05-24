#İlkin Soydaş 1231602055
#kodumda bazen yapay zeka desteği aldım, grafik çizdirmede yapay zekadan yardım almak zorunda kaldım.

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import time

# Döviz kurlarını CollectAPI'den çeker
def get_currency_rates():
    url = "https://api.collectapi.com/economy/allCurrency"
    headers = {
        'content-type': "application/json",
        'authorization': "apikey YOUR_API_KEY"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        messagebox.showerror("Request Error", f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"Generic error occurred: {err}")
        messagebox.showerror("Error", f"Generic error occurred: {err}")

    return None

# Altın kurlarını CollectAPI'den çeker
def get_gold_rates():
    url = "https://api.collectapi.com/economy/goldPrice"
    headers = {
        'content-type': "application/json",
        'authorization': "apikey YOUR_API_KEY"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        messagebox.showerror("Request Error", f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"Generic error occurred: {err}")
        messagebox.showerror("Error", f"Generic error occurred: {err}")

    return None

# Veritabanını başlatır ve tabloları oluşturur
def init_db():
    conn = sqlite3.connect('finances.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS assets (
                      id INTEGER PRIMARY KEY,
                      date TEXT,
                      asset_type TEXT,
                      amount REAL,
                      rate REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                      id INTEGER PRIMARY KEY,
                      asset_id INTEGER,
                      transaction_date TEXT,
                      transaction_type TEXT,
                      transaction_amount REAL,
                      transaction_rate REAL,
                      cost REAL,
                      FOREIGN KEY (asset_id) REFERENCES assets (id))''')
    conn.commit()
    conn.close()

# FreeCurrencyAPI ile geçmiş döviz kurlarını çeker
def get_historical_rates(currency_code, days=30):
    base_url = "https://api.freecurrencyapi.com/v1/historical"
    api_key = "YOUR_API_KEY"
    
    today = datetime.now()
    end_date = today - timedelta(days=1)
    start_date = end_date - timedelta(days=days)
    
    all_dates = []
    all_rates = []
    
    try:
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if current_date > end_date:
                print(f"Skipping date beyond end_date: {date_str}")
                current_date += timedelta(days=1)
                continue
                
            params = {
                'apikey': api_key,
                'date': date_str,
                'base_currency': 'TRY',
                'currencies': currency_code
            }
            
            print(f"Fetching data for {date_str}")
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and date_str in data['data']:
                try:
                    rate = 1 / float(data['data'][date_str][currency_code])
                    all_dates.append(current_date)
                    all_rates.append(rate)
                except (KeyError, ValueError) as e:
                    print(f"Error processing rate for date {date_str}: {e}")
            
            time.sleep(0.5)
            current_date += timedelta(days=1)
        
        if all_dates and all_rates:
            sorted_data = sorted(zip(all_dates, all_rates), key=lambda x: x[0])
            dates, rates = zip(*sorted_data)
            
            print(f"Successfully fetched {len(dates)} days of data")
            return {
                'success': True,
                'result': [
                    {
                        'date': date.strftime("%Y-%m-%d"),
                        'selling': f"{rate:.4f}"
                    } for date, rate in zip(dates, rates)
                ]
            }
        else:
            print("No valid data points found")
            messagebox.showerror("Hata", "Geçerli veri noktası bulunamadı")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        messagebox.showerror("Hata", f"Veri çekilirken bağlantı hatası oluştu: {e}")
        return None
    except Exception as err:
        print(f"Unexpected error: {err}")
        messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {err}")
        return None

# Ana finans uygulamasını temsil eden sınıf
class FinanceApp:
    # Uygulama arayüzünü başlatır
    def __init__(self, root):
        self.root = root
        self.root.title("Portföy Yönetim Uygulaması")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.top_frame = ttk.Frame(root)
        self.top_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.middle_frame = ttk.Frame(root)
        self.middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.style = ttk.Style()
        self.style.configure('Treeview', font=('Helvetica', 16))
        self.style.configure('Treeview.Heading', font=('Helvetica', 18))
        self.style.configure('W.TCombobox', arrowsize=60)
        root.option_add("*TCombobox*Listbox*Font", 24)
        
        self.create_widgets()
        
        init_db()
        self.update_pie_chart()
        self.update_current_rates()

        self.asset_combobox = None

    # Uygulama arayüzündeki widgetları oluşturur
    def create_widgets(self):
        self.amount_label = tk.Label(self.middle_frame, text="Miktar:", font=("Helvetica", 20))
        self.amount_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.amount_entry = tk.Entry(self.middle_frame, font=("Helvetica", 20))
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        self.asset_label = tk.Label(self.middle_frame, text="Varlık Tipi (USD, EUR, GBP, Gram Altın, Çeyrek Altın, Yarım Altın, Tam Altın):", font=("Helvetica", 18))
        self.asset_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.asset_entry = tk.Entry(self.middle_frame, font=("Helvetica", 20))
        self.asset_entry.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        
        self.add_button = tk.Button(self.middle_frame, text="Varlık Ekle", command=self.add_asset, 
                                  font=("Helvetica", 18), bg='light blue')
        self.add_button.grid(row=2, column=1, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.show_transactions_button = tk.Button(self.middle_frame, text="Geçmiş İşlemler", 
                                               command=self.show_transactions_window, 
                                               font=("Helvetica", 18), bg='light yellow')
        self.show_transactions_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        self.total_label = tk.Label(self.middle_frame, text="Toplam Varlığım: 0 TL", 
                                  font=("Helvetica", 20), bg='orange')
        self.total_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.currency_label = tk.Label(self.top_frame, text="Döviz Kurları:", font=("Helvetica", 20, "bold"))
        self.currency_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5)
        
        self.currency_tree = ttk.Treeview(self.top_frame, columns=("currency", "buying", "selling"), 
                                        show="headings", height=3)
        self.currency_tree.heading("currency", text="Döviz")
        self.currency_tree.heading("buying", text="Alış")
        self.currency_tree.heading("selling", text="Satış")
        self.currency_tree.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.graph_label = tk.Label(self.top_frame, text="Döviz Grafiği:", font=("Helvetica", 20, "bold"))
        self.graph_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)
        
        combobox_frame = ttk.Frame(self.top_frame)
        combobox_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        self.currency_combobox = ttk.Combobox(combobox_frame, values=["USD", "EUR", "GBP"], 
                                            state="readonly", font=("Helvetica", 16), width=10)
        self.currency_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.currency_combobox.set("USD")
        
        self.period_combobox = ttk.Combobox(combobox_frame, values=["1 Gün", "7 Gün", "30 Gün"], 
                                          state="readonly", font=("Helvetica", 16), width=10)
        self.period_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.period_combobox.set("7 Gün")
        
        self.update_graph_button = tk.Button(combobox_frame, text="Grafiği Güncelle", 
                                          command=self.update_currency_graph,
                                          font=("Helvetica", 16))
        self.update_graph_button.grid(row=0, column=2, padx=5, pady=5)
        
        combobox_frame.grid_columnconfigure(0, weight=1)
        combobox_frame.grid_columnconfigure(1, weight=1)
        combobox_frame.grid_columnconfigure(2, weight=1)
        
        self.progressbar = ttk.Progressbar(self.top_frame, mode='indeterminate', length=100)
        self.progressbar.place_forget()

        self.fig_currency, self.ax_currency = plt.subplots(figsize=(12, 4))
        self.canvas_currency = FigureCanvasTkAgg(self.fig_currency, master=self.top_frame)
        self.canvas_currency.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.bottom_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

    # Güncel döviz ve altın kurlarını günceller
    def update_current_rates(self):
        rates = get_currency_rates()
        if rates is None:
            return
            
        for item in self.currency_tree.get_children():
            self.currency_tree.delete(item)
            
        currencies_to_show = ["USD", "EUR", "GBP"]
        for currency in rates['result']:
            if currency['code'] in currencies_to_show:
                self.currency_tree.insert("", "end", values=(
                    currency['code'],
                    f"{float(currency['buying']):.4f}",
                    f"{float(currency['selling']):.4f}"
                ))

    # API yüklenirken gösterilecek pop-up penceresini oluşturur ve gösterir
    def show_loading_popup(self):
        if hasattr(self, 'loading_window') and self.loading_window is not None and self.loading_window.winfo_exists():
            return

        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Yükleniyor")
        self.loading_window.geometry("5x5")
        self.loading_window.withdraw()

        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        self.loading_window.resizable(False, False)
        
        loading_label = tk.Label(self.loading_window, text="KUR BİLGİSİ YÜKLENİYOR", font=("Helvetica", 14), fg="black", bg="white")
        loading_label.pack(pady=10)
        
        loading_progressbar = ttk.Progressbar(self.loading_window, mode='indeterminate', length=150)
        loading_progressbar.pack()
        loading_progressbar.start()
        
        self.loading_window.protocol("WM_DELETE_WINDOW", lambda: None)

        self.loading_window.update_idletasks()
        self.loading_window.update()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.loading_window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.loading_window.deiconify()
        self.loading_window.lift()
        self.loading_window.focus_force()

    # Yükleniyor pop-up penceresini kapatır
    def hide_loading_popup(self):
        if hasattr(self, 'loading_window') and self.loading_window is not None and self.loading_window.winfo_exists():
            self.loading_window.grab_release()
            self.loading_window.destroy()
        self.loading_window = None
            
    # Seçilen para birimi için tarihsel grafiği günceller
    def update_currency_graph(self):
        if not hasattr(self, 'currency_combobox') or self.currency_combobox is None:
            messagebox.showerror("Hata", "Para birimi seçimi bulunamadı!")
            return
            
        selected_currency = self.currency_combobox.get()
        if not selected_currency:
            messagebox.showerror("Hata", "Lütfen bir para birimi seçin!")
            return
        
        self.show_loading_popup()

        period = self.period_combobox.get()
        days = 1 if period == "1 Gün" else 7 if period == "7 Gün" else 30
        
        historical_data = get_historical_rates(selected_currency, days)

        self.hide_loading_popup()

        if historical_data is None or 'result' not in historical_data:
            return
            
        dates = []
        rates = []
        
        for item in historical_data['result']:
            dates.append(datetime.strptime(item['date'], "%Y-%m-%d"))
            rates.append(float(item['selling']))
            
        self.ax_currency.clear()
        self.ax_currency.plot(dates, rates, marker='o', linestyle='-', color='blue')
        self.ax_currency.set_title(f"{selected_currency} Kuru - Son {days} Gün")
        self.ax_currency.set_xlabel('Tarih')
        self.ax_currency.set_ylabel('Kur (TL)')
        self.ax_currency.grid(True)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self.canvas_currency.draw()

    # Varlık ekleme işlemini yapar
    def add_asset(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Yanlış Giriş!", "Miktar olarak sadece sayı girilmeli. (1, 1.5, 0.5 gibi..)")
            return

        asset_type = self.asset_entry.get().upper()

        rates = get_currency_rates()
        if rates is None:
            return

        try:
            rate = next(item['selling'] for item in rates['result'] if item['code'] == asset_type)
        except StopIteration:
            gold_rates = get_gold_rates()
            if gold_rates is None:
                return
            try:
                rate = next(item['selling'] for item in gold_rates['result'] if item['name'].upper() == asset_type)
            except StopIteration:
                messagebox.showerror("Hata", f"Yanlış varlık tipi girdiniz {asset_type}")
                return

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cost = rate

        conn = sqlite3.connect('finances.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO assets (date, asset_type, amount, rate) VALUES (?, ?, ?, ?)", (date, asset_type, amount, rate))
        asset_id = cursor.lastrowid
        cursor.execute("INSERT INTO transactions (asset_id, transaction_date, transaction_type, transaction_amount, transaction_rate, cost) VALUES (?, ?, ?, ?, ?, ?)", (asset_id, date, 'buy', amount, rate, cost))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Varlık başarıyla eklendi!")
        self.update_pie_chart()
        self.update_transactions_table(None)

    # Geçmiş işlemler penceresini gösterir
    def show_transactions_window(self):
        transactions_window = tk.Toplevel(self.root)
        transactions_window.title("Geçmiş İşlemler")
        transactions_window.geometry("1400x1000")

        asset_label = tk.Label(transactions_window, text="İşlem geçmişi görmek için varlık tipi seçiniz:", font=("Helvetica", 18))
        asset_label.grid(row=0, column=0, padx=10, pady=10)

        conn = sqlite3.connect('finances.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT asset_type FROM assets")
        rows = cursor.fetchall()
        conn.close()

        asset_types = sorted([row[0] for row in rows])
        self.asset_combobox = ttk.Combobox(transactions_window, values=asset_types, font=("Helvetica", 16), state="readonly")
        self.asset_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.asset_combobox.bind("<<ComboboxSelected>>", self.update_transactions_table)

        self.transactions_tree = ttk.Treeview(transactions_window, columns=("date", "amount", "profit_loss_percentage", "profit_loss_tl", "days_passed", "cost"))
        self.transactions_tree.heading("date", text="Alım Tarihi", anchor=tk.CENTER)
        self.transactions_tree.heading("amount", text="Alım Miktarı", anchor=tk.CENTER)
        self.transactions_tree.heading("profit_loss_percentage", text="Kar/Zarar (%)", anchor=tk.CENTER)
        self.transactions_tree.heading("profit_loss_tl", text="Kar/Zarar (TL)", anchor=tk.CENTER)
        self.transactions_tree.heading("days_passed", text="Geçen Gün", anchor=tk.CENTER)
        self.transactions_tree.heading("cost", text="Maliyet (adet Başı)", anchor=tk.CENTER)
        self.transactions_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.transactions_tree.column("date", width=200)
        self.transactions_tree.column("amount", width=150)
        self.transactions_tree.column("profit_loss_percentage", width=150)
        self.transactions_tree.column("profit_loss_tl", width=150)
        self.transactions_tree.column("days_passed", width=150)
        self.transactions_tree.column("cost", width=150)

        self.transactions_tree.column("#0", width = 0, stretch = "no")

        tree_scroll = ttk.Scrollbar(transactions_window, orient="vertical", command=self.transactions_tree.yview)
        tree_scroll.grid(row=1, column=2, sticky="ns")
        self.transactions_tree.configure(yscrollcommand=tree_scroll.set)

        self.total_profit_loss_label = tk.Label(transactions_window, text="", font=("Helvetica", 14))
        self.total_profit_loss_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.update_transactions_table(None)

        transactions_window.grid_columnconfigure(0, weight=1)
        transactions_window.grid_columnconfigure(1, weight=1)
        transactions_window.grid_rowconfigure(1, weight=1)

        self.fig_transactions, self.ax_transactions = plt.subplots(figsize=(12, 4))
        self.canvas_transactions = FigureCanvasTkAgg(self.fig_transactions, master=transactions_window)
        self.canvas_transactions.get_tk_widget().grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    # İşlem geçmişi tablosunu günceller
    def update_transactions_table(self, event):
        if self.asset_combobox is None:
            return

        selected_asset = self.asset_combobox.get()

        conn = sqlite3.connect('finances.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT transactions.transaction_date, transactions.transaction_amount, transactions.transaction_rate,
                transactions.cost, assets.rate
            FROM transactions INNER JOIN assets ON transactions.asset_id = assets.id
            WHERE assets.asset_type = ?
            ORDER BY transactions.transaction_date DESC
        """, (selected_asset,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return

        self.transactions_tree.delete(*self.transactions_tree.get_children())

        rates = get_currency_rates()
        if rates is None:
            return
        gold_rates = get_gold_rates()
        if gold_rates is None:
            return

        total_profit_loss_percentage = 0
        total_profit_loss_tl = 0

        for row in rows:
            transaction_date = row[0]
            transaction_amount = row[1]
            transaction_rate = row[2]
            cost = row[3]
            asset_rate = row[4]

            current_rate = next((item['selling'] for item in rates['result'] if item['code'] == selected_asset), None)
            if current_rate is None:
                current_rate = next((item['selling'] for item in gold_rates['result'] if item['name'].upper() == selected_asset), None)

            if current_rate is not None:
                profit_loss_percentage = ((current_rate - transaction_rate) / transaction_rate) * 100
                profit_loss_tl = (current_rate - transaction_rate) * transaction_amount
            else:
                profit_loss_percentage = 0
                profit_loss_tl = 0

            total_profit_loss_percentage += profit_loss_percentage
            total_profit_loss_tl += profit_loss_tl

            days_passed = (datetime.now() - datetime.strptime(transaction_date, "%Y-%m-%d %H:%M:%S")).days

            if profit_loss_tl > 0.00:
                bg_color = 'pale green'
            elif profit_loss_tl < 0.00:
                bg_color = 'light coral'
            else:
                bg_color = 'white'

            self.transactions_tree.insert("", tk.END, values=(transaction_date, transaction_amount, f"{profit_loss_percentage:.2f}", f"{profit_loss_tl:.2f}", days_passed, f"{cost:.2f}"), tags=('colored',))
            self.transactions_tree.tag_configure('colored', background=bg_color)

        self.total_profit_loss_label.config(text=f"Toplam Kar/Zarar: {total_profit_loss_percentage:.2f}%  &  {total_profit_loss_tl:.2f} TL", font=('Helvetica', 18))

        self.update_pie_chart_transactions(selected_asset)

    # Varlık dağılımını gösteren pie chart'ı günceller
    def update_pie_chart(self):
        conn = sqlite3.connect('finances.db')
        cursor = conn.cursor()
        cursor.execute("SELECT asset_type, SUM(amount * rate) as total_value FROM assets GROUP BY asset_type")
        rows = cursor.fetchall()
        conn.close()

        asset_types = [f"{row[0]} ({row[1]:.2f} TL)" for row in rows]
        total_values = [row[1] for row in rows]

        total_value = sum(total_values)

        self.total_label.config(text=f"Toplam Varlığım: {total_value:.2f} TL")

        self.ax.clear()
        wedges, texts, autotexts = self.ax.pie(total_values, labels=asset_types, autopct='%1.1f%%', startangle=140)

        for text in texts + autotexts:
            text.set_fontsize(14)

        plt.tight_layout()

        self.canvas.draw()

    # İşlem geçmişi pie chart'ını günceller
    def update_pie_chart_transactions(self, asset_type):
        conn = sqlite3.connect('finances.db')
        cursor = conn.cursor()
        cursor.execute("SELECT transactions.transaction_amount, transactions.transaction_rate FROM transactions INNER JOIN assets ON transactions.asset_id = assets.id WHERE assets.asset_type = ?", (asset_type,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return

        transaction_amounts = [row[0] for row in rows]
        transaction_rates = [row[1] for row in rows]

        daily_values = []
        for i in range(len(transaction_amounts)):
            daily_value = transaction_amounts[i] * transaction_rates[i]
            daily_values.append(daily_value)

        self.ax_transactions.clear()

        self.ax_transactions.plot(daily_values, marker='o', linestyle='-', color='b', label='Günlük TL Değeri')
        self.ax_transactions.set_title(f"{asset_type} için Günlük TL Değeri")
        self.ax_transactions.set_xlabel('İşlem Indexi')
        self.ax_transactions.set_ylabel('TL Değeri')
        self.ax_transactions.legend()

        plt.tight_layout()
        self.canvas_transactions.draw()

    # Uygulama kapatılırken onay alır
    def on_closing(self):
        if messagebox.askokcancel("Kapat", "Uygulama kapatılıyor, emin misiniz?"):
            self.root.quit()


root = tk.Tk()
# Finans uygulamasını başlatır
app = FinanceApp(root)
root.mainloop()
