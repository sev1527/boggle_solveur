from tkinter import Tk, Button, Label, Frame, Entry
from tkinter.ttk import Progressbar, Treeview, Scrollbar

VERSION = "1.2.1"

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
        
        Label(self, text=f"Solveur de Boggle {VERSION}  ", font="Arial 35").pack()
        
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
        self.bouton = Button(self, text="Voir les possibilités", command=self.valider, width=100, height=2, bg="light green", state="disabled")
        self.bouton.pack()
        
        self.after(100, self.init)
    
    def init(self):
        barre = Progressbar(self, length=600)
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
        TYPE = list(TYPE)
        BANNI = []
        barre.step(10)
        self.update()
        def supprime_accent(texte):
            accents = {'a': ['à', 'ã', 'á', 'â'],
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
        self.MOTS, self.MOTS_C, self.TYPE = MOTS, MOTS_C, TYPE
        self.bouton.config(state="normal")
    
    def entree_modifiee(self, l, c):
        self.plateau[l][c].delete(0, "end")
        c += 1
        if c==4:
            c = 0
            l += 1
        if l!=4:
            self.plateau[l][c].focus_set()
        self.after(100, self.majuscules)

    def majuscules(self):
        for l in self.plateau:
            for e in l:
                txt = e.get()
                e.delete(0, "end")
                e.insert(0, txt.upper())

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
        tree = Treeview(self.fra, columns=("mot", "longueur", "type"), height=21)
        tree.heading("#0", text="Classement")
        tree.column("#0", width=150)
        tree.heading("mot", text="Mot")
        tree.heading("longueur", text="Longueur")
        tree.column("longueur", width=100)
        tree.heading("type", text="Type")
        scroll = Scrollbar(self.fra, orient="vertical", command=tree.yview)
        tree.config(yscrollcommand=scroll.set)
        tree.pack(side="left")
        scroll.pack(side="left", fill="y")
        
        for resultat, compteur in zip(resultats, range(len(resultats))):
            tree.insert("", "end", text=compteur, values=(resultat, len(resultat), self.TYPE[self.MOTS.index(resultat.lower())]))
            self.update()
        
        self.bouton.config(state="normal")

if __name__ == "__main__":
    Fen().mainloop()
