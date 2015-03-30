import os,re
REFERENCE = {   '19':"négation",
                '22':"juron",
                '121':"social",
                '123':"ami",
                '125':"affect",
                '126':"émopos",
                '127':"émonég",
                '128':"anxiété",
                '129':"colère",
                '130':"tristesse",
                '134':"divergence",
                '149':"sexualité",
                '355':"accomplissement",
                '462':"consentement",
                '463':"hésitation",
                '464':"remplisseur",}

class LexicTreeElement(object):
    def __init__(self):
        self.children = dict()
        self.values   = None
        
    def add(self,word,*values):
        # On est arrivé au bout du mot, on stocke les valeurs
        if not len(word):
            self.values = values
        # Il reste des lettres
        else : 
            # Pas d'enfant pour la lettre suivante, on le cree
            if word[0] not in self.children.keys() :
                self.children[word[0]] = LexicTreeElement()
            # On s'appelle recursivement sur l'enfant
            self.children[word[0]].add(word[1:],*values)
            
    def test(self,word):
        if not len(word): return self.values
        if '*' in self.children.keys() : return self.children['*'].values
        if word[0] not in self.children.keys() : return None
        return self.children[word[0]].test(word[1:])
        
class LiwcAction(object):
    def __init__(self,filename,path="FrenchLIWCDic_words.txt"):
        """ Initialise l'arbre contenant le dico liwc et le dictionnaire de résultats """
        # Sauvegarde du prefixe de fichiers
        self.filename=filename
        # Création de l'élément racine
        self.tree = LexicTreeElement()
        # Ouverture du dictionnaire
        with open(path,encoding="utf-8-sig") as _file : 
            for _n,_line in enumerate(_file) : 
                _data = _line.rstrip().split("\t")
                 # On teste si le mot appartient aux champs lexicaux choisis
                if len(set(_data) & set(REFERENCE.keys())) :
                    # On ajoute le mot courant dans l'arbre
                    self.tree.add(*_data)
        # Création du dictionnaire de résultats
        self.results = dict()
        
    def do(self,line,index):
        """ Test si les mots de line est dans l'arbre liwc"""
        # On découpe la ligne en mots
        _splitLine = re.split('\W+', line, flags = re.UNICODE)
        # On normalise chaque mot en minuscule
        for _word in (_w.lower() for _w in _splitLine) :
            # On teste le mot
            _res = self.tree.test(_word)
            # Si le test est positif (_res != None)
            if _res is not None :
                # Si le mot n'est pas dans le dico de résultats, on l'ajoute
                if _word not in self.results.keys(): self.results[_word]=1
                # Sinon on incrémente le compteur d'occurences
                else : self.results[_word]+=1
                    
    def finalize(self):
        """ Création du fichier de résultat """
        # Création du nom de fichier
        _filePath = "{}_liwc.csv".format(self.filename)
        _liwcFile = open(_filePath,'w')
        # On ecrit les mots et les occurences résultat
        for _k,_v in self.results.items() :
            _liwcFile.write('{};{};{}\n'.format(_k,_v,self.tree.test(_k)))
        _liwcFile.close()
        # Test d'existence
        return os.path.exists(_filePath)
