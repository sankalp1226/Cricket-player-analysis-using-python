import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class SearchBox(ttk.Entry):
    def __init__(self, parent, players, command, *args, **kwargs):
        ttk.Entry.__init__(self, parent, *args, **kwargs)
        self.players = players
        self.command = command
        self.filtered_players = []
        self.suggestion_window = None
        
        # Bind events
        self.bind('<KeyRelease>', self.on_key_release)
        self.bind('<FocusOut>', self.on_focus_out)
        self.bind('<Return>', self.on_return)
    
    def show_suggestions(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
        
        if not self.filtered_players:
            return
        
        # Create suggestion window
        self.suggestion_window = tk.Toplevel()
        self.suggestion_window.overrideredirect(True)
        
        # Position window below search box
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.suggestion_window.geometry(f"+{x}+{y}")
        
        # Create listbox for suggestions
        listbox = tk.Listbox(self.suggestion_window, width=self.winfo_width())
        listbox.pack(fill='both', expand=True)
        
        # Add suggestions to listbox
        for player in self.filtered_players:
            listbox.insert('end', player)
        
        # Bind selection
        listbox.bind('<<ListboxSelect>>', lambda e: self.select_player(listbox))
        
        # Limit height based on number of suggestions
        height = min(len(self.filtered_players), 5)
        listbox.configure(height=height)
    
    def select_player(self, listbox):
        if not listbox.curselection():
            return
        selection = listbox.get(listbox.curselection())
        self.delete(0, 'end')
        self.insert(0, selection)
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.command(selection)
    
    def on_key_release(self, event):
        # Get current text
        text = self.get().lower()
        
        # Filter players
        self.filtered_players = [
            player for player in self.players 
            if text and text in player.lower()
        ]
        
        # Show suggestions
        self.show_suggestions()
    
    def on_focus_out(self, event):
        # Delay destruction to allow for selection
        if self.suggestion_window:
            self.after(100, self.destroy_suggestion_window)
    
    def destroy_suggestion_window(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
    
    def on_return(self, event):
        text = self.get()
        if text in self.players:
            self.command(text)
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

class CricketAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Match Analysis")
        self.root.geometry("1200x800")
        
        # Load data
        try:
            self.batting_data = pd.read_csv('batting_summary.csv')
            self.bowling_data = pd.read_csv('bowling_summary.csv')
            print("Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {e}")
            return
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_player_analysis_tab()
        self.create_team_analysis_tab()
        self.create_match_analysis_tab()
        self.create_performance_trends_tab()
    
    def create_player_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Player Analysis")
        
        # Player selection frame
        select_frame = ttk.LabelFrame(tab, text="Search Player", padding="5")
        select_frame.pack(fill='x', padx=5, pady=5)
        
        # Create search box with auto-suggestions
        players = sorted(self.batting_data['Batsman_Name'].unique())
        ttk.Label(select_frame, text="Search:").pack(side='left', padx=5)
        self.search_box = SearchBox(select_frame, players, self.update_player_analysis)
        self.search_box.pack(side='left', padx=5, fill='x', expand=True)
        
        # Stats display frame
        self.player_stats_frame = ttk.Frame(tab)
        self.player_stats_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_team_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Team Analysis")
        
        # Team selection frame
        select_frame = ttk.LabelFrame(tab, text="Select Teams", padding="5")
        select_frame.pack(fill='x', padx=5, pady=5)
        
        teams = sorted(self.batting_data['Team_Innings'].unique())
        
        ttk.Label(select_frame, text="Team 1:").pack(side='left', padx=5)
        self.team1_var = tk.StringVar()
        team1_cb = ttk.Combobox(select_frame, textvariable=self.team1_var, values=teams)
        team1_cb.pack(side='left', padx=5)
        
        ttk.Label(select_frame, text="Team 2:").pack(side='left', padx=5)
        self.team2_var = tk.StringVar()
        team2_cb = ttk.Combobox(select_frame, textvariable=self.team2_var, values=teams)
        team2_cb.pack(side='left', padx=5)
        
        ttk.Button(select_frame, text="Compare", command=self.update_team_analysis).pack(side='left', padx=5)
        
        # Team stats frame
        self.team_stats_frame = ttk.Frame(tab)
        self.team_stats_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_match_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Match Analysis")
        
        # Match selection frame
        select_frame = ttk.LabelFrame(tab, text="Select Match", padding="5")
        select_frame.pack(fill='x', padx=5, pady=5)
        
        matches = sorted(self.batting_data['Match_Between'].unique())
        ttk.Label(select_frame, text="Match:").pack(side='left', padx=5)
        self.match_var = tk.StringVar()
        match_cb = ttk.Combobox(select_frame, textvariable=self.match_var, values=matches)
        match_cb.pack(side='left', padx=5)
        match_cb.bind('<<ComboboxSelected>>', self.update_match_analysis)
        
        # Match stats frame
        self.match_stats_frame = ttk.Frame(tab)
        self.match_stats_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_performance_trends_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Performance Trends")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(tab, text="Select Analysis", padding="5")
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        analysis_types = ["Batting Averages", "Bowling Economy", "Team Win Rates"]
        self.trend_var = tk.StringVar(value=analysis_types[0])
        for analysis in analysis_types:
            ttk.Radiobutton(controls_frame, text=analysis, value=analysis, 
                          variable=self.trend_var, command=self.update_trends).pack(side='left', padx=5)
        
        # Trends display frame
        self.trends_frame = ttk.Frame(tab)
        self.trends_frame.pack(fill='both', expand=True, padx=5, pady=5)

    def update_player_analysis(self, player):
        if not player:
            return

        # Normalize player name: strip whitespace, convert to title case
        player = player.strip().title()

        # Create case-insensitive search DataFrames
        batting_stats = self.batting_data[self.batting_data['Batsman_Name'].str.strip().str.title() == player]
        bowling_stats = self.bowling_data[self.bowling_data['Bowler_Name'].str.strip().str.title() == player]

        # Clear previous stats
        for widget in self.player_stats_frame.winfo_children():
            widget.destroy()

        # Check if player exists in either batting or bowling data
        if batting_stats.empty and bowling_stats.empty:
            # If no exact match, try partial matching
            batting_partial = self.batting_data[self.batting_data['Batsman_Name'].str.contains(player, case=False, na=False)]
            bowling_partial = self.bowling_data[self.bowling_data['Bowler_Name'].str.contains(player, case=False, na=False)]

            if batting_partial.empty and bowling_partial.empty:
                # No matches found at all
                error_label = ttk.Label(
                    self.player_stats_frame, 
                    text=f"No data found for '{player}'. \nCheck player name spelling.", 
                    foreground='red', 
                    justify='center'
                )
                error_label.pack(pady=10)

                # Suggest similar names
                all_players = set(
                    list(self.batting_data['Batsman_Name'].str.strip().str.title().unique()) + 
                    list(self.bowling_data['Bowler_Name'].str.strip().str.title().unique())
                )
                similar_players = [p for p in all_players if player.lower() in p.lower()]
                
                if similar_players:
                    suggestion_label = ttk.Label(
                        self.player_stats_frame, 
                        text="Did you mean one of these players?\n" + "\n".join(similar_players[:5]), 
                        foreground='blue'
                    )
                    suggestion_label.pack(pady=5)
                
                return

            # Use partial matches if found
            batting_stats = batting_partial
            bowling_stats = bowling_partial

        # Batting Analysis
        if not batting_stats.empty:
            total_runs = batting_stats['Runs'].sum()
            matches = len(batting_stats)
            avg = total_runs / matches if matches > 0 else 0
            highest_score = batting_stats['Runs'].max()

            # Create figure for batting performance
            fig_batting = plt.Figure(figsize=(10, 6))

            # Batting runs plot
            ax1 = fig_batting.add_subplot(121)
            ax1.bar(batting_stats['Match_no'], batting_stats['Runs'])
            ax1.set_title(f'{player} - Batting Performance')
            ax1.set_xlabel('Match Number')
            ax1.set_ylabel('Runs')
            ax1.tick_params(axis='x', rotation=45)

            # Batting strike rate plot
            ax2 = fig_batting.add_subplot(122)
            ax2.plot(batting_stats['Match_no'], batting_stats['Strike_Rate'], marker='o')
            ax2.set_title(f'{player} - Strike Rate')
            ax2.set_xlabel('Match Number')
            ax2.set_ylabel('Strike Rate')
            ax2.tick_params(axis='x', rotation=45)

            # Embed the plot in Tkinter
            canvas_batting = FigureCanvasTkAgg(fig_batting, master=self.player_stats_frame)
            canvas_batting.draw()
            canvas_batting.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Batting stats summary
            stats_text = f"""
            Batting Statistics for {player}:
            Total Matches: {matches}
            Total Runs: {total_runs}
            Average: {avg:.2f}
            Highest Score: {highest_score}
            """
            stats_label = ttk.Label(self.player_stats_frame, text=stats_text, justify='left')
            stats_label.pack(pady=10)

        # Bowling Analysis
        if not bowling_stats.empty:
            total_wickets = bowling_stats['Wickets'].sum()
            matches = len(bowling_stats)
            economy_rate = bowling_stats['Runs'].sum() / bowling_stats['Overs'].sum() if bowling_stats['Overs'].sum() > 0 else 0
            best_bowling = bowling_stats.loc[bowling_stats['Wickets'].idxmax()]

            # Create figure for bowling performance
            fig_bowling = plt.Figure(figsize=(10, 6))

            # Bowling wickets plot
            ax1 = fig_bowling.add_subplot(121)
            ax1.bar(bowling_stats['Match_no'], bowling_stats['Wickets'])
            ax1.set_title(f'{player} - Bowling Performance')
            ax1.set_xlabel('Match Number')
            ax1.set_ylabel('Wickets')
            ax1.tick_params(axis='x', rotation=45)

            # Bowling economy plot
            ax2 = fig_bowling.add_subplot(122)
            ax2.plot(bowling_stats['Match_no'], bowling_stats['Economy'], marker='o')
            ax2.set_title(f'{player} - Economy Rate')
            ax2.set_xlabel('Match Number')
            ax2.set_ylabel('Economy Rate')
            ax2.tick_params(axis='x', rotation=45)

            # Embed the plot in Tkinter
            canvas_bowling = FigureCanvasTkAgg(fig_bowling, master=self.player_stats_frame)
            canvas_bowling.draw()
            canvas_bowling.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Bowling stats summary
            bowling_text = f"""
            Bowling Statistics for {player}:
            Total Matches: {matches}
            Total Wickets: {total_wickets}
            Economy Rate: {economy_rate:.2f}
            Best Bowling: {best_bowling['Wickets']} wickets for {best_bowling['Runs']} runs
            """
            bowling_label = ttk.Label(self.player_stats_frame, text=bowling_text, justify='left')
            bowling_label.pack(pady=10)
    
    def update_team_analysis(self):
        team1 = self.team1_var.get()
        team2 = self.team2_var.get()
        
        if not team1 or not team2:
            return
            
        # Clear previous stats
        for widget in self.team_stats_frame.winfo_children():
            widget.destroy()
            
        # Calculate team stats
        team1_stats = self.calculate_team_stats(team1)
        team2_stats = self.calculate_team_stats(team2)
        
        # Create comparison plots
        fig = plt.Figure(figsize=(12, 6))
        
        # Batting comparison
        ax1 = fig.add_subplot(121)
        teams = [team1, team2]
        avg_runs = [team1_stats['avg_runs'], team2_stats['avg_runs']]
        ax1.bar(teams, avg_runs)
        ax1.set_title("Average Team Runs")
        ax1.set_ylabel("Runs")
        
        # Bowling comparison
        ax2 = fig.add_subplot(122)
        avg_economy = [team1_stats['avg_economy'], team2_stats['avg_economy']]
        ax2.bar(teams, avg_economy)
        ax2.set_title("Average Team Economy")
        ax2.set_ylabel("Economy Rate")
        
        # Display stats
        stats_text = f"""
        Team Comparison:
        
        {team1}:
        Average Runs: {team1_stats['avg_runs']:.2f}
        Average Economy: {team1_stats['avg_economy']:.2f}
        
        {team2}:
        Average Runs: {team2_stats['avg_runs']:.2f}
        Average Economy: {team2_stats['avg_economy']:.2f}
        """
        ttk.Label(self.team_stats_frame, text=stats_text, justify='left').pack(pady=10)
        
        # Add the plots
        canvas = FigureCanvasTkAgg(fig, self.team_stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def calculate_team_stats(self, team):
        team_batting = self.batting_data[self.batting_data['Team_Innings'] == team]
        team_bowling = self.bowling_data[self.bowling_data['Bowling_Team'] == team]
        
        avg_runs = team_batting.groupby('Match_no')['Runs'].sum().mean()
        avg_economy = team_bowling['Economy'].mean()
        
        return {
            'avg_runs': avg_runs,
            'avg_economy': avg_economy
        }
    
    def update_match_analysis(self, event=None):
        match = self.match_var.get()
        if not match:
            return
            
        # Clear previous stats
        for widget in self.match_stats_frame.winfo_children():
            widget.destroy()
            
        # Get match data
        match_batting = self.batting_data[self.batting_data['Match_Between'] == match]
        match_bowling = self.bowling_data[self.bowling_data['Match_Between'] == match]
        
        # Create figure for match analysis
        fig = plt.Figure(figsize=(12, 6))
        
        # Team scores comparison
        ax1 = fig.add_subplot(121)
        team_scores = match_batting.groupby('Team_Innings')['Runs'].sum()
        team_scores.plot(kind='bar', ax=ax1)
        ax1.set_title("Team Scores")
        ax1.set_ylabel("Runs")
        
        # Top performers
        ax2 = fig.add_subplot(122)
        top_batsmen = match_batting.nlargest(5, 'Runs')[['Batsman_Name', 'Runs']]
        top_batsmen.plot(kind='barh', x='Batsman_Name', y='Runs', ax=ax2)
        ax2.set_title("Top 5 Batsmen")
        
        # Display match summary
        summary_text = f"""
        Match Summary: {match}
        
        Team Scores:
        {team_scores.to_string()}
        
        Top Scorer: {top_batsmen.iloc[0]['Batsman_Name']} ({top_batsmen.iloc[0]['Runs']} runs)
        """
        ttk.Label(self.match_stats_frame, text=summary_text, justify='left').pack(pady=10)
        
        # Add the plots
        canvas = FigureCanvasTkAgg(fig, self.match_stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_trends(self):
        analysis_type = self.trend_var.get()
        
        # Clear previous trends
        for widget in self.trends_frame.winfo_children():
            widget.destroy()
            
        fig = plt.Figure(figsize=(12, 6))
        
        if analysis_type == "Batting Averages":
            self.plot_batting_trends(fig)
        elif analysis_type == "Bowling Economy":
            self.plot_bowling_trends(fig)
        else:  # Team Win Rates
            self.plot_team_trends(fig)
            
        canvas = FigureCanvasTkAgg(fig, self.trends_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_batting_trends(self, fig):
        # Calculate match-wise batting averages
        match_averages = self.batting_data.groupby('Match_no')['Runs'].mean()
        
        ax = fig.add_subplot(111)
        match_averages.plot(kind='line', ax=ax)
        ax.set_title("Tournament Batting Average Trend")
        ax.set_xlabel("Match Number")
        ax.set_ylabel("Average Runs")
    
    def plot_bowling_trends(self, fig):
        # Calculate match-wise bowling economy
        match_economy = self.bowling_data.groupby('Match_no')['Economy'].mean()
        
        ax = fig.add_subplot(111)
        match_economy.plot(kind='line', ax=ax, color='green')
        ax.set_title("Tournament Bowling Economy Trend")
        ax.set_xlabel("Match Number")
        ax.set_ylabel("Economy Rate")
    
    def plot_team_trends(self, fig):
        # This is a simplified version - in real analysis, you'd need to determine match winners
        team_runs = self.batting_data.groupby(['Match_no', 'Team_Innings'])['Runs'].sum()
        team_runs = team_runs.unstack()
        
        ax = fig.add_subplot(111)
        team_runs.plot(kind='line', ax=ax)
        ax.set_title("Team Performance Trends")
        ax.set_xlabel("Match Number")
        ax.set_ylabel("Team Total Runs")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = CricketAnalyzer(root)
    root.mainloop()
