import pandas as pd

def read_epw(epw_file):
    """
    Lit un fichier météo EPW et renvoie un DataFrame contenant la température extérieure et le rayonnement global horaire.
    - epw_file : chemin du fichier EPW (str) ou fichier ouvert en mode texte/binaire.
    """
    # Colonnes utiles du format EPW (voir documentation EnergyPlus EPW)
    col_names = ["Year", "Month", "Day", "Hour", "Minute", "T_ext", "GlobRad"]
    use_columns = [0, 1, 2, 3, 4, 6, 13]
    # Lecture du fichier en sautant les 8 lignes d'en-tête
    df = pd.read_csv(epw_file, skiprows=8, header=None, names=col_names, usecols=use_columns)
    # Génération d'une colonne datetime pour chaque heure
    start_year = int(df.loc[0, "Year"])
    # La première heure du fichier EPW correspond à 01:00 le 1er janvier de l'année de départ
    start_timestamp = f"{start_year}-01-01 01:00"
    df['datetime'] = pd.date_range(start=start_timestamp, periods=len(df), freq='H')
    # Conserver uniquement les colonnes pertinentes
    df = df[['datetime', 'T_ext', 'GlobRad']]
    return df
