import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import os
import mysql.connector
from getpass import getpass
import re

#Stored Procedures
sp_varer_i_varelager = "VisVarelager"
sp_allekunder = "AlleKunder"
sp_fjernkunde = "FjernKunde"
sp_fjernkundeto = "FjernKundeTo"
sp_leggtilkunde = "LeggTilKunde"
sp_listalleordre = "ListAlleOrdrer"
sp_totalsalgperordre = "TotalSalgPerOrdre"
sp_visordredetaljer = "VisOrdreDetaljer"
sp_visvarelager = "VisVarelager"

#midlertidige variabler
conn = "temp"
input_ordrenummer = "0"
kundenummer_entry = "temp"
valid = "temp"

global db_user, db_password, db_host, db_name, db_port

#Passordhåndtering
def prompt_for_credentials():

    # Opprett en ny dialogvindu for inndata
    dialog = tk.Tk()
    dialog.title("Database innlogging")
    dialog.geometry("200x300") 

    # Felt for brukernavn
    tk.Label(dialog, text="Brukernavn:").pack()
    db_user_entry = tk.Entry(dialog)
    db_user_entry.pack()
    db_user_entry.insert(0, str("root"))   
    
    # Felt for passord
    tk.Label(dialog, text="Passord:").pack()
    db_password_entry = tk.Entry(dialog, show='*')
    db_password_entry.pack()

    # Felt for database-server
    tk.Label(dialog, text="Database-server:").pack()
    db_host_entry = tk.Entry(dialog)
    db_host_entry.pack()
    db_host_entry.insert(0, str("localhost"))
    
    # Felt for database-navn
    tk.Label(dialog, text="Database:").pack()
    db_name_entry = tk.Entry(dialog)
    db_name_entry.pack()
    db_name_entry.insert(0, str("varehusdb"))

    # Felt for portnummer
    tk.Label(dialog, text="Portnummer:").pack()
    db_port_entry = tk.Entry(dialog)
    db_port_entry.pack()
    db_port_entry.insert(0, int("3306"))

    # En funksjon for å håndtere når brukeren trykker på 'Ok'-knappen
    def on_ok():

        global db_user, db_password, db_host, db_name, db_port
        # Hent verdier fra Entry-widgets og oppdater globale variabler
        db_user = db_user_entry.get()
        db_password = db_password_entry.get()
        db_host = db_host_entry.get()
        db_name = db_name_entry.get()
        db_port = db_port_entry.get()

        dialog.destroy()
       

    # Ok og Avbryt knapper
    tk.Button(dialog, text="Ok", command=on_ok).pack()
    tk.Button(dialog, text="Avbryt", command=dialog.destroy).pack()

    dialog.mainloop()

prompt_for_credentials()

# Classes for å formatere output fra databasen 

class class_Vare:
    def __init__(self, varenummer, navn, antall, pris):
        self.varenummer = varenummer
        self.navn = navn
        self.antall = antall
        self.pris = pris
    def __str__(self):
        return f"{self.varenummer} - {self.navn} - {self.antall} - {self.pris}"
    #Denne funksjonen sier noe om hvordan outputen blir formatert når de blir omgjort til strings.

class class_Ordre:
    def __init__(self, OrdreNr, OrdreDato, SendtDato, BetaltDato, KNr):
         self.Ordrenummer = OrdreNr
         self.Ordre = OrdreDato
         self.SendtDato = SendtDato
         self.BetaltDato = BetaltDato
         self.Kundenummer = KNr

    def __str__(self):
        return f"{self.Ordrenummer} - {self.Ordre} - {self.Ordre} - {self.SendtDato} - {self.BetaltDato} - {self.Kundenummer}"
    #Denne funksjonen sier noe om hvordan outputen blir formatert når de blir omgjort til strings.
    
class class_Ordredetaljer:
    def __init__(self, VNr, Betegnelse, Antall, PrisPrEnhet, TotalSolgtPrisPerVare, KNr, Navn, Adresse, TotaltSalgsSum):
         self.Varenummer = VNr
         self.Betegnelse = Betegnelse
         self.Antall = Antall
         self.PrisPrEnhet = PrisPrEnhet
         self.TotalSolgtPrisPerVare = TotalSolgtPrisPerVare
         self.Kundenummer = KNr
         self.Navn = Navn
         self.Adresse = Adresse
         self.TotaltSalgsSum = TotaltSalgsSum
    def __str__(self):
         return f"{self.Varenummer} - {self.Betegnelse} - {self.Antall} - {self.PrisPrEnhet} - {self.TotalSolgtPrisPerVare} - {self.Kundenummer} - {self.Navn} - {self.Adresse} - {self.TotaltSalgsSum}"
    #Denne funksjonen sier noe om hvordan outputen blir formatert når de blir omgjort til strings.
        
class class_visallekunder:
    def __init__(self, KNr, Fornavn, Etternavn, Adresse, PostNr):
         self.Kundenummer = KNr
         self.Fornavn = Fornavn
         self.Etternavn = Etternavn
         self.Adresse = Adresse
         self.PostNr = PostNr
    def __str__(self):
         return f"{self.Kundenummer} - {self.Fornavn} {self.Etternavn} - {self.Adresse} - {self.PostNr}"
    #Denne funksjonen sier noe om hvordan outputen blir formatert når de blir omgjort til strings.
    
# input-valideringsfunksjoner
def valider_fornavn(fornavn):
    pattern = r'^[a-zøæåA-ZØÆÅ -]{1,50}$'
    if re.match(pattern, fornavn):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig fornavn. Vennligst bruk kun bokstaver, mellomrom og bindestrek (1-50 tegn).")
        return False

def valider_etternavn(etternavn):
    pattern = r'^[a-zøæåA-ZØÆÅ -]{1,50}$'
    if re.match(pattern, etternavn):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig etternavn. Vennligst bruk kun bokstaver, mellomrom og bindestrek (1-50 tegn).")
        return False

def valider_adresse(adresse):
    pattern = r'^[a-zøæåA-ZØÆÅ0-9 -]{1,50}$'
    if re.match(pattern, adresse):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig adresse. Vennligst bruk kun bokstaver, tall, mellomrom og bindestrek (1-50 tegn).")
        return False

def valider_postnummer(postnummer):
    pattern = r'^[0-9]{4}$'  
    if re.match(pattern, postnummer):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig postnummer. Postnummeret må være fire siffer.")
        return False

def valider_kundenummer(kundenummer):
    pattern = r'^[0-9]{4}$'    
    if re.match(pattern, kundenummer):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig kundenummer. Kundenummeret må være fire siffer.")
        return False

def valider_ordrenummer(ordrenummer):
    pattern = r'^[0-9]{5}$'    
    if re.match(pattern, ordrenummer):
        return True
    else:
        messagebox.showerror("Feil", "Ugyldig ordrenummer. Ordrenummeret må være fem siffer.")
        return False

 
#Funksjonene bak "List alle varer på lager - knappen"
def vare_db_til_objekt(varetupplefradb: tuple):
    #Mappe tupler til objekter
    return class_Vare(
        varenummer = varetupplefradb[0],
        navn = varetupplefradb[1],
        antall = varetupplefradb[2],
        pris = varetupplefradb[3],
        )
     
def list_varelager():
    cursor = conn.cursor()
    cursor.callproc(sp_varer_i_varelager)
    varer = []

    for result in cursor.stored_results():
        varetupplerfradb = result.fetchall()
        for varetupple in varetupplerfradb:
            vare = vare_db_til_objekt(varetupple)
            varer.append(vare)
    print("list_varelager er kjørt")
  
    return varer

def update_output_varelager():
    data = list_varelager()
    output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
    for item in data:
        output_field.insert(tk.END, str(item) + "\n")
        

    # 1. Mapper touples fra databasen til spesifikke objekter
    # 1.1 Henter verdiene fra Class Vare
    # 1.2 Populerer variablene fra Class Vare til varetouplesfradb[0] - [3]
        #Eksempel: Dette er sånn at Varenummer får den første verdien fra touplen (der informasjonen om varenummer faktisk ligger).
    # kobler seg til databasen og lager en cursor (?)
    ## kjører den spesifikke stored proceduresn 
    # Lager en tom liste som heter varer
    #For-loop som henter resultatene fra stored-proceduren:
        #Varetupplerfradb = alle verdier
            #deler alle verdiene inn i kolonner basert på toupler (en tuple er en kolonne)
            # vare = kjør mappe-funksjonen på hver varetupple
            # vareer.append(vare) = legg de i listen vare.
    # mapper resultatet til objekter
    # returner objekten
    # def update_output_varelager(): tømmer ouput, og fyller den med innholdet fra list_varelager    
         
#Funksjonene bak "List alle ordre - knappen"

def ordre_db_til_objekt(ordretupplefradb: tuple):
    return class_Ordre(
        OrdreNr = ordretupplefradb[0],
        OrdreDato = ordretupplefradb[1],
        SendtDato = ordretupplefradb[2],
        BetaltDato = ordretupplefradb[3],
        KNr = ordretupplefradb[4],
        )

def list_alle_ordrer():
    cursor = conn.cursor()
    cursor.callproc(sp_listalleordre)
    ordrer = []

    for result in cursor.stored_results():
         ordretupplerfradb = result.fetchall()
         for ordretupple in ordretupplerfradb:
              ordre = ordre_db_til_objekt(ordretupple)
              ordrer.append(ordre)
    print("list_alle_ordrer er kjørt")

    return ordrer
    
def update_output_alle_ordrer():
    data = list_alle_ordrer()
    output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
    for item in data:
        output_field.insert(tk.END, str(item) + "\n")

#Funksjonene bak "List innhold i ordre - knappen"


def ordredetaljer_db_til_objekt(ordredetaljertupple: tuple):
    return class_Ordredetaljer(
         VNr = ordredetaljertupple[0],
         Betegnelse = ordredetaljertupple[1],
         Antall = ordredetaljertupple[2],
         PrisPrEnhet = ordredetaljertupple[3],
         TotalSolgtPrisPerVare = ordredetaljertupple[4],
         KNr = ordredetaljertupple[5],
         Navn = ordredetaljertupple[6],
         Adresse = ordredetaljertupple[7],
         TotaltSalgsSum = ordredetaljertupple[8],
        )

def vise_innhold_i_ordre():
    output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
    input_ordrenummer = input_entry.get()


    if not input_ordrenummer:
        output_field.insert(tk.END, "Skriv ordrenummeret du ønsker å se innholdet i i Input-feltet øverst, og trykk på ""List innhold i ordre"" \n")
    else:
        #sjekker om den er et tall mellom 0 og 99999 
        if valider_ordrenummer(input_ordrenummer):
            output_field.insert(tk.END, f"Valid ordrenummer: {input_ordrenummer}\n")
        else:
            output_field.insert(tk.END, "Ordrenummeret må være et nummer mellom 0 og 99999")

    
    
    cursor = conn.cursor()   
    cursor.callproc(sp_visordredetaljer, (input_ordrenummer,))
    ordredetaljer = []


    for result in cursor.stored_results():
        ordredetaljetupplerfradb = result.fetchall()
        for ordredetaljtupple in ordredetaljetupplerfradb:
            ordredetaljer.append(ordredetaljer_db_til_objekt(ordredetaljtupple))
    
    return ordredetaljer


def update_output_vise_innhold_i_ordre():
    data = vise_innhold_i_ordre()
    output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
    for item in data:
        output_field.insert(tk.END, str(item) + "\n")

#PLACEHOLDER FOR Funksjonene bak "Generer Faktura"

def generere_faktura():
    print("Button 4 clicked")
    messagebox.showerror("Feil", "Funksjonen for å generere fakturaer er kun aktivert i PRO-versjonen. \n" + " Oppgrader her: https://www.nettside.net/kjøp/")
    
    #frvillig del om å generere fakture

# Funksjonene bak "Generer faktura " | ikke ferdig // Frivillig oppgave

def update_output_vise_faktura():
        data = generere_faktura()
        output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
        for item in data:
            output_field.insert(tk.END, item + "\n")

# Funksjonene bak "Vis alle kunder - knappen" | ferdig

def kunder_db_til_objekt(visallekundertupplerfradb: tuple):
    return class_visallekunder(
        KNr = visallekundertupplerfradb[0],
        Fornavn = visallekundertupplerfradb[1],
        Etternavn = visallekundertupplerfradb[2],
        Adresse = visallekundertupplerfradb[3],
        PostNr = visallekundertupplerfradb[4],
        )
            
def vis_alle_kunder():
    cursor = conn.cursor()
    cursor.callproc(sp_allekunder)
    allekunder = []

    for result in cursor.stored_results():
        visallekundertupplerfradb = result.fetchall()
        for allekundertupple in visallekundertupplerfradb:
            kunder = kunder_db_til_objekt(allekundertupple)
            allekunder.append(kunder)
    print("vis_alle_kunder er kjørt")
  
    return allekunder

def update_output_vis_alle_kunder():
        data = vis_alle_kunder()
        output_field.delete('1.0', tk.END)  # Rydder vekk gammelt innhold fra output fielden
        for item in data:
            output_field.insert(tk.END, str(item) + "\n")


#funksjonene bak "Legg til kunde - knappen" 

def open_popup_legg_til_kunde():
   
    def legg_til_kunde_nestekundenr():
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(KNr) from kunde")
        siste_kundenummer = cursor.fetchone()[0]
        neste_kundenummer = siste_kundenummer + 1 if siste_kundenummer else 1
        Kundenummer_entry.delete(0, tk.END)
        Kundenummer_entry.insert(0, int(neste_kundenummer))
        return neste_kundenummer
           
        
    popup_legg_til_kunde = tk.Toplevel(root)
    popup_legg_til_kunde.title("Legg til kunde")
    popup_legg_til_kunde.geometry("400x400")

    # Definer output felt
    Kundenummer_label = ttk.Label(popup_legg_til_kunde, text="Kundenummer:")
    Kundenummer_label.grid(row=0, column=0, padx=5, pady=5)
    Kundenummer_entry = ttk.Entry(popup_legg_til_kunde)
    Kundenummer_entry.grid(row=0, column=1, padx=5, pady=5)
    
     
    # Generer neste kundenummer og auto-fyll kundenummer-feltet
    legg_til_kunde_nestekundenr()

    # Definer input felt
    Fornavn_label = ttk.Label(popup_legg_til_kunde, text="Fornavn:")
    Fornavn_label.grid(row=1, column=0, padx=5, pady=5)
    Fornavn_entry = ttk.Entry(popup_legg_til_kunde)
    Fornavn_entry.grid(row=1, column=1, padx=5, pady=5)
    
    Etternavn_label = ttk.Label(popup_legg_til_kunde, text="Etternavn:")
    Etternavn_label.grid(row=2, column=0, padx=5, pady=5)
    Etternavn_entry = ttk.Entry(popup_legg_til_kunde)
    Etternavn_entry.grid(row=2, column=1, padx=5, pady=5)

    Adresse_label = ttk.Label(popup_legg_til_kunde, text="Adresse:")
    Adresse_label.grid(row=3, column=0, padx=5, pady=5)
    Adresse_entry = ttk.Entry(popup_legg_til_kunde)
    Adresse_entry.grid(row=3, column=1, padx=5, pady=5)

    PostNr_label = ttk.Label(popup_legg_til_kunde, text="Postnummer:")
    PostNr_label.grid(row=4, column=0, padx=5, pady=5)
    PostNr_entry = ttk.Entry(popup_legg_til_kunde)
    PostNr_entry.grid(row=4, column=1, padx=5, pady=5)

    # Knapp for å submitte input
    submit_button = ttk.Button(popup_legg_til_kunde, text="Legg til", command=lambda: popup_legg_til_kunde_submit(
        Kundenummer_entry.get(), 
        Fornavn_entry.get(),
        Etternavn_entry.get(), 
        Adresse_entry.get(), 
        PostNr_entry.get(), 
        ))
    submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def popup_legg_til_kunde_submit(Kundenummer, Fornavn, Etternavn, Adresse, Postnummer):
        # Valider inndataene
        if not valider_kundenummer(Kundenummer):
            return
        if not valider_fornavn(Fornavn):
            return
        if not valider_etternavn(Etternavn):
            return
        if not valider_adresse(Adresse):
            return
        if not valider_postnummer(Postnummer):
            return

        # Inndataene er gyldige, legg til kunden i databasen
        data = (Kundenummer, Fornavn, Etternavn, Adresse, Postnummer)
        cursor = conn.cursor()
        try:
            cursor.callproc(sp_leggtilkunde, data)
            conn.commit()
            # Vis bekreftelsesmelding som popup-vindu
            message = f"{Fornavn} {Etternavn} er nå lagt til som kunde"
            messagebox.showinfo("Success", message)
            # Lukk popup-vinduet
            popup_legg_til_kunde.destroy()
        except Exception as e:
            messagebox.showerror("Feil", f"Feil oppstod: {str(e)}")
        finally:
            cursor.close()
          

#Funksjonene bak "Slett kunde - knappen" | ferdig
def open_popup_slett_kunde(): 

    popup_slett_kunde = tk.Toplevel(root)
    popup_slett_kunde.title("Slett kunde")
    popup_slett_kunde.geometry("400x400") 
 
    # Definer input fields
    Kundenummer_label = ttk.Label(popup_slett_kunde, text="Kundenummer:")
    Kundenummer_label.grid(row=0, column=0, padx=5, pady=5)
    Kundenummer_entry = ttk.Entry(popup_slett_kunde)
    Kundenummer_entry.grid(row=0, column=1, padx=5, pady=5)
   

    # Knapp for å submitte input
    submit_button = ttk.Button(popup_slett_kunde, text="Slett kunde", command=lambda: popup_slett_kunde_submit(
        Kundenummer_entry.get(), 
        ))
    submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def popup_slett_kunde_submit(Kundenummer):
        if not valider_kundenummer(Kundenummer):
            return
        try:
            # Hent fornavn og etternavn til kunden som skal slettes
            cursor = conn.cursor()
            cursor.execute("SELECT Fornavn, Etternavn FROM kunde WHERE KNr = %s", (Kundenummer,))
            slettet_navn = cursor.fetchone()
            
            if slettet_navn:
                slettet_fornavn, slettet_etternavn = slettet_navn
                
                # Vis bekreftelsesmelding som popup-vindu
                message = f"{Kundenummer} {slettet_fornavn} {slettet_etternavn} er nå slettet fra kundedatabasen"    
                messagebox.showinfo("Success", message)
                # Lukk popup-vinduet
                popup_slett_kunde.destroy()
            else:
                messagebox.showwarning("Feil", "Kunden ble ikke funnet.")

            # Slett kunden fra databasen
            data = (Kundenummer,)
            cursor.callproc(sp_fjernkundeto, data)
            conn.commit()
        except Exception as e:
            messagebox.showerror("Feil", f"Feil oppstod: {str(e)}")
        finally:
            cursor.close()


   


# lager hoved-vinduet
root = tk.Tk()
root.title("Tverrfaglig Prosjekt - Database-GUI")
root.geometry("800x400")  

# Lager en hoved frame for å holde input fielden midt på øverst
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

# Input field midt på øverst
input_label = ttk.Label(main_frame, text="Enter something:")
input_label.pack(side=tk.LEFT, padx=5)
input_entry = ttk.Entry(main_frame)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Frames for buttons og output under input fielden
lower_frame = ttk.Frame(root)
lower_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Frame for buttons på venstresiden
button_frame = ttk.Frame(lower_frame, padding="10 10 10 10")
button_frame.pack(side=tk.LEFT, fill=tk.Y, anchor='n')

# Frame for output på høyresiden
output_frame = ttk.Frame(lower_frame, padding="10 10 10 10")
output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Buttons
button1 = ttk.Button(button_frame, text="List alle varer på lager", command=update_output_varelager)
button1.pack(pady=5, fill=tk.X)

button2 = ttk.Button(button_frame, text="List alle ordre(r)", command=update_output_alle_ordrer)
button2.pack(pady=5, fill=tk.X)

button3 = ttk.Button(button_frame, text="List innhold i ordre", command=update_output_vise_innhold_i_ordre)
button3.pack(pady=5, fill=tk.X)

button4 = ttk.Button(button_frame, text="Generer faktura", command=update_output_vise_faktura)
button4.pack(pady=5, fill=tk.X)

button5 = ttk.Button(button_frame, text="Vis alle kunder", command=update_output_vis_alle_kunder)
button5.pack(pady=5, fill=tk.X)

button6 = ttk.Button(button_frame, text="Legg til kunde", command=open_popup_legg_til_kunde)
button6.pack(pady=5, fill=tk.X)

button6 = ttk.Button(button_frame, text="Slett kunde", command=open_popup_slett_kunde)
button6.pack(pady=5, fill=tk.X)

# Output field (høyre side)
output_field = tk.Text(output_frame, wrap=tk.WORD, width=50)
output_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=output_field.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
output_field['yscrollcommand'] = scrollbar.set



if __name__ == "__main__":
    
    
    try:
        # Setter opp databasetilkoblingen
        conn = mysql.connector.connect(
            host=db_host,
            database=db_name,
            #port=db_port,
            user=db_user,
            password=db_password
        )
        
        if conn.is_connected():
            print('Tilkoblingen til databasen var vellykket!')
        else:
             print('Kunne ikke koble til databasen')
             exit(1)
        




        root.mainloop()   
        
        
    finally:
        
        if conn.is_connected():
            conn.close()
            #For å ikke skrive passordet til databasen i klartekst!
            #FOR Å RESETTE ENVIROMENT VARIABLE:
            # Clear the db_password environment variable
            if 'db_password' in os.environ:
                os.environ.pop('db_password')
                print("db_password variablen er tømt.")
            else:
                print("db_password var ikke satt.")
            print('Database connection is closed')

        
