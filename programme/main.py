from tkinter import Tk, Button, Label, Frame, Entry, Menu
from tkinter.ttk import Progressbar, Treeview, Scrollbar
from copy import deepcopy
import webbrowser

VERSION = "1.3.1"

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

def _chercher(MOTS_C, mot, x, y, vus, carte):
    prox = []
    for p in [[x, y-1], [x, y+1], [x-1, y], [x+1, y], [x-1, y-1], [x-1, y+1], [x+1, y-1], [x+1, y+1]]:
        if p[0] in range(4) and p[1] in range(4) and not p in vus:
            prox.append(p)
    if not prox:
        return []
    res = []
    for p in prox:
        try:
            nmot = mot + carte[p[0]][p[1]]
            if nmot.lower() in MOTS_C[nmot.lower()[0:5]]:
                res += [nmot] + _chercher(MOTS_C, nmot, p[0], p[1], vus+[[x, y]], carte)
            res += _chercher(MOTS_C, nmot, p[0], p[1], vus+[[x, y]], carte)
        except KeyError:
            pass
    return res

def chercher(MOTS_C, grille, barre, step):
    res = []
    for l in range(len(grille)):
        for c in range(len(grille[l])):
            res += _chercher(MOTS_C, grille[l][c], l, c, [], grille)
            barre.step(step)
            barre.update()
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
        
        Label(self, text=f"Solveur de Boggle {VERSION}  ", font="Arial 25").pack()
        
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
        self.bouton = Button(self, text="Voir les possibilités", command=self.valider, font="Arial 20", width=30, height=1, bg="light green", state="disabled")
        self.bouton.pack()
        
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
            if c==4:
                c = 0
                l += 1
            if l!=4:
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
    
    def valider(self):
        try:
            self.fra.destroy()
        except AttributeError:
            pass
        self.bouton.config(state="disabled")
        p = Progressbar(self, length=400)
        p.pack()
        t = []
        for l in self.plateau:
            t.append([])
            for c in l:
                t[-1].append(c.get())
        resultats = list(reversed(chercher(self.MOTS_C, t, p, 100/16)))
        
        p.destroy()
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
        
        for resultat, compteur in zip(resultats, range(len(resultats))):
            self.tree.insert("", "end", text=compteur, values=(resultat, len(resultat)))
            self.update()
        
        self.resultats = resultats
        self.bouton.config(state="normal")
        self.tree.bind("<Button-3>", self.clic_droit)

if __name__ == "__main__":
    Fen().mainloop()
