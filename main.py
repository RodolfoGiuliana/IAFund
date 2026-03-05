import yfinance as yf
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import customtkinter as ctk

# Database Fondi AcomeA (Esempio di mappatura ISIN -> Simbolo Yahoo)
# Nota: Molti fondi italiani sono mappati su Yahoo Finance con .MI o .TI
FONDI_ACOMEA = {
    "AcomeA Breve Termine": "IT0001265325.MI",
    "AcomeA Italia": "IT0000381040.MI",
    "AcomeA Europa": "IT0000381016.MI",
    "AcomeA America": "IT0004718437.MI",
}

class RoboAdvisorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Investment Analytics Pro - Institutional Suite")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # UI Elements
        self.label = ctk.CTkLabel(self, text="AI Portfolio Rebalancer", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        self.btn_run = ctk.CTkButton(self, text="Analizza e Ricalibra Portafoglio", command=self.run_analysis)
        self.btn_run.pack(pady=10)

        self.result_box = ctk.CTkTextbox(self, width=600, height=300)
        self.result_box.pack(pady=20)

    def run_analysis(self):
        self.result_box.insert("end", "Connessione ai mercati in corso...\n")
        
        tickers = list(FONDI_ACOMEA.values())
        
        # 1. Download Dati Storici
        data = yf.download(tickers, period="3y")['Adj Close']
        
        # 2. Calcolo Parametri Quantitativi
        mu = expected_returns.mean_historical_return(data)
        S = risk_models.sample_cov(data)

        # 3. Ottimizzazione (Markowitz - Max Sharpe Ratio)
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        # 4. Output Istituzionale
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "--- REPORT DI RICALIBRAZIONE IA ---\n\n")
        for fondo, ticker in FONDI_ACOMEA.items():
            w = cleaned_weights.get(ticker, 0)
            self.result_box.insert("end", f"{fondo}: {w*100:.2f}%\n")
        
        perf = ef.portfolio_performance(verbose=False)
        self.result_box.insert("end", f"\n Rendimento Atteso: {perf[0]*100:.2f}%")
        self.result_box.insert("end", f"\n Volatilità Annua: {perf[1]*100:.2f}%")
        self.result_box.insert("end", f"\n Sharpe Ratio: {perf[2]:.2f}")

if __name__ == "__main__":
    app = RoboAdvisorApp()
    app.mainloop()
