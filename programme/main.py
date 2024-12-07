# -*- coding: utf-8 -*-
"""
Une fenêtre graphique pour résoudre les grille de Boggle.
Créé par sev1527.
https://github.com/sev1527/boggle_solveur
"""
from tkinter import Tk, Button, Label, Frame, Entry, Menu
from tkinter.ttk import Progressbar, Treeview, Scrollbar
from tkinter.messagebox import askyesno, showinfo, showwarning
from tkinter.simpledialog import askstring
from copy import deepcopy
import webbrowser
from requests import get
from time import time
from random import shuffle, randint

VERSION = "1.5"

DES = """SFEIHE
FAIRXO
EIRWUL
KOTEUN
CAMPDE
TAIEOA
QJMABO
LGNUYE
CASREL
RISENH
ENITGV
SRIMAO
RBTILA
TONSED
AVENDZ
SUTPEL"""
DES = DES.split("\n")

TYPES = {
    "A": "adjectif",
    "ADV": "adverbe",
    "INTJ": "interjection",
    "N": "nom",
    "V": "verbe",
    "ms": "masculin singulier",
    "mp": "masculin pluriel",
    "fs": "féminin singulier",
    "fp": "féminin pluriel",
    "Kms": "participe passé masculin singulier",
    "Kmp": "participe passé masculin pluriel",
    "Kfs": "participe passé féminin singulier",
    "Kfp": "participe passé féminin pluriel",
    "G": "participe présent",
    "W": "infinitif",
}
BANNI = ["PFX", "PFX+z1", "PFX+z2"]
for temps in [["F", " du futur"], ["C", " du conditionnel"], ["I", " de l'imparfait"], ["J", " du passé simple"], ["P", " du présent"], ["S", " du subjonctif"], ["T", " de l'imparfait du subjonctif"], ["Y", " de l'impératif"]]:
    for personne in [["1s", "1ère du s."], ["2s", "2ème du s."], ["3s", "3ème du s."], ["1p", "1ère du p."], ["2p", "2ème du p."], ["3p", "3ème du p."]]:
        TYPES[temps[0]+personne[0]] = personne[1] + temps[1]

def trier(liste):
    ret = []
    for i in liste:
        fin = True
        for p, i_ligne in zip(ret, range(len(ret))):
            if len(i) < len(p):
                ret.insert(i_ligne, i)
                fin = False
                break
        if fin:
            ret.append(i)
    return ret

def _chercher(MOTS_C, mot, x, y, vus, carte, mx, my):
    prox = []
    for p in [[x, y-1], [x, y+1], [x-1, y], [x+1, y], [x-1, y-1], [x-1, y+1], [x+1, y-1], [x+1, y+1]]:
        if p[0] in range(my) and p[1] in range(mx) and not p in vus:
            prox.append(p)
    if not prox:
        return []
    res = []
    for p in prox:
        try:
            nmot = mot + carte[p[0]][p[1]]
            if nmot.lower() in MOTS_C[nmot.lower()[0:5]]:
                res += [nmot] + _chercher(MOTS_C, nmot, p[0], p[1], vus+[[x, y]], carte, mx, my)
            res += _chercher(MOTS_C, nmot, p[0], p[1], vus+[[x, y]], carte, mx, my)
        except KeyError:
            pass
    return res

def _cherchera(MOTS_C, mot, x, y, vus, carte, mx, my, barre):
    prox = []
    for p in [[x, y-1], [x, y+1], [x-1, y], [x+1, y], [x-1, y-1], [x-1, y+1], [x+1, y-1], [x+1, y+1]]:
        if p[0] in range(my) and p[1] in range(mx) and not p in vus:
            prox.append(p)
    if not prox:
        return []
    res = []
    for p in prox:
        try:
            nmot = mot + carte[p[0]][p[1]]
            res += _chercher(MOTS_C, nmot, p[0], p[1], vus+[[x, y]], carte, mx, my)
        except KeyError:
            pass
        barre.step(1/len(prox)*1/(mx*my)*100)
        barre.update()
    return res

def chercher(MOTS_C, grille, barre, obj):
    res = []
    for l in range(len(grille)):
        for c in range(len(grille[l])):
            res += _cherchera(MOTS_C, grille[l][c], l, c, [], grille, len(grille[0]), len(grille), barre)
            if obj.annule:
                return ["annulé"]
    return trier(list(set(res)))

def fonction(fonct, *args, **kwargs):
    """
    Transforme une fonction en lambda.
    """
    def retour(*_):
        fonct(*args, **kwargs)
    return retour


class Fen(Tk):
    """
    La fenêtre principale du programme.
    """
    def __init__(self):
        super().__init__()
        self.title("Solveur de Boggle")
        
        frame = Frame(self)
        frame.pack()
        Label(frame, text=f"Solveur de Boggle {VERSION}  ", font="Arial 25").pack(side="left")
        Button(frame, text="🗘", command=self.mise_a_jour).pack(side="left")
        Button(frame, text="🎲", command=self.melanger).pack(side="left")
        Button(frame, text="🔎", command=self.recherche).pack(side="left")
        Button(frame, text="ⓘ", command=self.a_propos).pack(side="left")
        
        self.plateau = []
        for l in range(4):
            self.plateau.append([])
            frame = Frame(self)
            frame.pack()
            for c in range(4):
                entre = Entry(frame, font="arial 30", width=2)
                entre.bind("<KeyPress>", fonction(self.entree_modifiee, l, c))
                entre.pack(side="left")
                self.plateau[-1].append(entre)
        self.bouton = Button(self, text="Voir les possibilités", command=self.valider, font="Arial 20", width=30, height=1, bg="light green")
        self.bouton.pack()
        self.verrouiller()
        
        self.message = Label(self, text="Chargement en cours de la base de données...")
        self.message.pack()
        
        self.after(100, self.init)
    
    def init(self):
        barre = Progressbar(self, length=500)
        barre.pack()
        self.update()
        f = open("mod.txt", encoding="UTF-8")
        barre.step(2)
        self.update()
        c = f.readlines()
        barre.step(5)
        self.update()
        f.close()
        barre.step(3)
        self.update()
        MOTS, TYPE = list(zip(*(i.split(".") for i in c)))
        barre.step(15)
        self.update()
        MOTS = list(MOTS)
        MOTS_O = deepcopy(MOTS)
        TYPE = list(TYPE)
        for i in range(len(TYPE)):
            TYPE[i] = TYPE[i].replace("\n", "")
        barre.step(10)
        self.update()
        def supprime_accent(texte):
            accents = {'a': ['à', 'ã', 'á', 'â'],
                       'c': ['ç'],
                       'e': ['é', 'è', 'ê', 'ë'],
                       'i': ['î', 'ï'],
                       'u': ['ù', 'ü', 'û'],
                       'o': ['ô', 'ö']}
            for (char, accented_chars) in accents.items():
                for accented_char in accented_chars:
                    texte = texte.replace(accented_char, char)
            return texte
        
        d = []
        ajout = len(MOTS)//55
        obj = ajout
        for i in range(len(MOTS)):
            MOTS[i] = supprime_accent(MOTS[i]).lower().split(",")[0]
            if TYPE[i] in BANNI:
                d.append(i)
            if i > obj:
                barre.step(1)
                self.update()
                obj += ajout
        dec = 0
        for i in d:
            del MOTS[i-dec]
            del MOTS_O[i-dec]
            del TYPE[i-dec]
            dec += 1
        self.update()
        MOTS_C = {}
        for mot in MOTS:
            try:
                MOTS_C[mot[0:5]].append(mot)
            except KeyError:
                MOTS_C[mot[0:5]] = [mot]
            for i in range(5):
                try:
                    MOTS_C[mot[0:i]]
                except KeyError:
                    MOTS_C[mot[0:i]] = []
        barre.destroy()
        self.MOTS, self.MOTS_C, self.MOTS_O, self.TYPE = MOTS, MOTS_C, MOTS_O, TYPE
        
        self.message.config(text="Chargement réussi !")
        self.deverrouiller()
        self.after(1000, fonction(self.mise_a_jour, False))
    
    def verrouiller(self):
        for ligne in self.plateau:
            for bouton in ligne:
                bouton.config(state="disabled")
        self.bouton.config(state="disabled")
        
    def deverrouiller(self):
        for ligne in self.plateau:
            for bouton in ligne:
                bouton.config(state="normal")
        self.bouton.config(state="normal")
        
    def entree_modifiee(self, l, c):
        self.update()
        self.after(10, fonction(self._entree_modifiee, l, c))
    
    def _entree_modifiee(self, l, c):
        if self.plateau[l][c].get():
            val = self.plateau[l][c].get()
            self.plateau[l][c].delete(0, "end")
            self.plateau[l][c].insert(0, val[-1])
            c += 1
            if c==len(self.plateau[l]):
                c = 0
                l += 1
            if l!=len(self.plateau):
                self.plateau[l][c].focus_set()
            else:
                self.bouton.flash()
        else:
            c -= 1
            if c==-1:
                c = 3
                l -= 1
            if l!=-1:
                self.plateau[l][c].focus_set()
        self.after(10, self.majuscules)

    def majuscules(self):
        for l in self.plateau:
            for e in l:
                txt = e.get()
                e.delete(0, "end")
                e.insert(0, txt.upper())

    def clic_droit(self, event):
        self.tree.selection_set(self.tree.identify_row(event.y))
        nb = self.tree.index(self.tree.selection()[0])
        m = Menu(self, tearoff=0)
        print(self.resultats[nb])
        vrai_mot = self.MOTS_O[self.MOTS.index(self.resultats[nb].lower())].split(",")
        m.add_command(label=vrai_mot[0], command=fonction(webbrowser.open, f"https://fr.wiktionary.org/wiki/{vrai_mot[0]}"))
        if vrai_mot[1]:
            m.add_command(label="->"+vrai_mot[1], command=fonction(webbrowser.open, f"https://fr.wiktionary.org/wiki/{vrai_mot[1]}"))
        m.add_separator()
        types = self.TYPE[self.MOTS.index(self.resultats[nb].lower())].split(":")
        mt = Menu(m, tearoff=0)
        m.add_cascade(label="Type", menu=mt)
        for t in types:
            non = True
            t2 = t.replace("\n", "").split("+")
            for type_o in TYPES:
                if type_o in t2:
                    mt.add_command(label=TYPES[type_o], state="disabled")
                    non = False
                    break
            if non:
                mt.add_command(label=t, state="disabled")
            print(t, t2)
        m.tk_popup(event.x_root, event.y_root)
    
    def annuler(self):
        self.annule = True
        self.deverrouiller()
        self.bouton_annuler.destroy()
    
    def valider(self):
        try:
            self.fra.destroy()
        except AttributeError:
            pass
        self.verrouiller()
        
        self.message.config(text="Analyse de la grille en cours, merci de patienter...")
        
        p = Progressbar(self, length=400)
        p.pack()
        
        self.annule = False
        self.bouton_annuler = Button(self, text="annuler", command=self.annuler, bg="red")
        self.bouton_annuler.pack()
        self.update()
        
        tdepart = time()
        t = []
        for l in self.plateau:
            t.append([])
            for c in l:
                t[-1].append(c.get())
        resultats = list(reversed(chercher(self.MOTS_C, t, p, self)))
        if resultats == ["annulé"]:
            self.message.config(text="Recherche annulée")
        else:
            self.message.config(text=f"Exécuté en {round(time()-tdepart)} secondes")
        
        p.destroy()
        self.bouton_annuler.destroy()
        self.update()
        
        self.fra = Frame(self)
        self.fra.pack()
        self.tree = Treeview(self.fra, columns=("mot", "longueur"), height=21)
        self.tree.heading("#0", text="Classement")
        self.tree.column("#0", width=150)
        self.tree.heading("mot", text="Mot")
        self.tree.heading("longueur", text="Longueur")
        self.tree.column("longueur", width=100)
        scroll = Scrollbar(self.fra, orient="vertical", command=self.tree.yview)
        self.tree.config(yscrollcommand=scroll.set)
        self.tree.pack(side="left")
        scroll.pack(side="left", fill="y")
        
        self.resultats = [] #Réponses sans les doubles
        base_u = [] #Liste des mots déjà trouvés
        compteur = 0
        for resultat in resultats:
            vrai_mot = self.MOTS_O[self.MOTS.index(resultat.lower())].split(",") #Recherche du mot accentué
            if vrai_mot[1]: #On regarde si il a une racine
                if vrai_mot[1] in base_u: # et on vérifie qu'elle n'a pas encore été utilisée
                    continue
                base_u.append(vrai_mot[1])
            else:
                if vrai_mot[0] in base_u:
                    continue
                base_u.append(vrai_mot[0])
            compteur += 1
            self.resultats.append(resultat)
            self.tree.insert("", "end", text=compteur, values=(resultat, len(resultat)))
            self.update()
        
        self.resultats_t = resultats #On crée une liste avec tous les résultats pour la recherche
        self.deverrouiller()
        self.tree.bind("<Button-3>", self.clic_droit)

    def melanger(self):
        liste = []
        for de in DES:
            liste.append(de[randint(0, 5)])
        shuffle(liste)
        i = 0
        for x in range(4):
            for y in range(4):
                self.plateau[x][y].delete(0, "end")
                self.plateau[x][y].insert(0, liste[i])
                i += 1

    def recherche(self):
        try:
            self.resultats_t
            mot = askstring("Mot à rechercher", "Entrez le mot que vous souhaitez rechercher sans faute d'orthographe :")
            if mot.upper() in self.resultats_t:
                showinfo("Valide", "Le mot a été trouvé.")
            else:
                showwarning("Incorrect", "Le mot n'a pas été trouvé.")
        except AttributeError:
            showwarning("Avertissement", "Avant de rechercher un mot, entrez et validez une grille.")

    def a_propos(self):
        if askyesno("À propos",
                    """Ce solveur de gille de Boggle a été créé par sev1527.
Souhaitez-vous ouvrir le dépôt GitHub pour en apprendre plus ?"""):
            webbrowser.open("https://github.com/sev1527/boggle_solveur")

    def mise_a_jour(self, manuel=True):
        """
        Bouton de demande de mise à jour pressé.
        """
        try:
            requ = get("https://raw.githubusercontent.com/sev1527/boggle_solveur/main/request.json",
                    timeout=(3 if manuel else 1))
            json = requ.json()
            print(json)
            n_l = "\n"
            if VERSION < json["update"]["last"]:
                if askyesno("Mise à jour",
                            f"""La version {json["update"]["last"]} est disponible"""\
                            f"""(vous avez {VERSION}).
Nouveautés :
{''.join(f'- {i}{n_l}' for i in json["update"]["new"])}

Souhaitez-vous ouvrir le dépôt GitHub pour l'installer ?"""):
                    webbrowser.open("https://github.com/sev1527/boggle_solveur")
            elif manuel:
                showinfo("Mise à jour", "Aucune mise à jour disponible.")
        except ConnectionError or TimeoutError:
            if manuel:
                showwarning("Échec", "Échec de la requête")

if __name__ == "__main__":
    Fen().mainloop()
