import pygame
import random
from collections import deque
from pygame.locals import *
class Uzel:
    def __init__(self,tabulka:list[int],hrac:int,posledni_pozice:int,hloubka:int):
        self.moznosti = []
        self.data = tabulka
        self.hrac = hrac
        self.posledni = posledni_pozice
        self.hloubka = hloubka
        for i in range(9):
            a = tri(tabulka[9*i:9*(i+1)])
            if a != 0:
                self.hodnota = a
                break
            self.hodnota = 0
def hledani_moznosti(tabulka:list,posledni:int):
    '''
    Funkce která vytvoří strom všech možných dalších tahů do hloubky 5 tahů. Pokud už strom je, tak se k němu jenom přidá do hloubky.
    Na vstupus je:
    tabulka: seznam délky 81 obsahující pouze prvky 0, 1 a -1. Reprezentuje aktuální pozici hry odkud hledáme
    posledni: číslo políčka (tj. mezi 0 a 80), kam bylo zahráno jako poslední
    '''
    global kontrola_komb
    hrac = -1*tabulka[posledni]
    k_udelani = deque()
    if tuple(tabulka) not in kontrola_komb.keys():#začínáme strom
        poc_hloubka = 0
        zacatek = Uzel(tabulka,hrac,posledni,poc_hloubka)
        k_udelani.append(zacatek)
        kontrola_komb[tuple(tabulka)] = zacatek
    else:#pouze prodlužujeme
        poc_hloubka = kontrola_komb[tuple(tabulka)].hloubka
        k_najiti = deque([kontrola_komb[tuple(tabulka)]])
        while k_najiti:
            aktualni = k_najiti.popleft()
            if aktualni.moznosti == []:
                k_udelani.append(aktualni)
            else:
                for c in aktualni.moznosti:
                    if c.posledni//9 == aktualni.posledni%9:
                        k_najiti.append(c)
    while k_udelani:
        aktualni = k_udelani.popleft()
        if aktualni.hodnota != 0:
            continue
        for pos in range(9*(aktualni.posledni%9),9*(aktualni.posledni%9)+9):
            if aktualni.data[pos] == 0:
                dalsi = aktualni.data[:]
                dalsi[pos] = aktualni.hrac
                if tuple(dalsi) in kontrola_komb:
                    dalsi_uzel = kontrola_komb[tuple(dalsi)]
                else:
                    dalsi_uzel = Uzel(dalsi,aktualni.hrac*-1,pos,aktualni.hloubka+1)
                    kontrola_komb[tuple(dalsi)] = dalsi_uzel
                    if dalsi_uzel.hloubka-poc_hloubka <= 4:
                        k_udelani.append(dalsi_uzel)
                aktualni.moznosti.append(dalsi_uzel)
def tri(tabulka:list[int]) -> int:
    '''
    Funkce, která zjistí, jestli jestli je v tabulce trojice stejných nenulových znaků v řadě, sloupci či diagonále
    tabulka: seznam délky 9 obsahující pouze prvky 0, 1 a -1. reprezentuje tabulku 3x3 ve které hledáme
    Na výstupu je buď 0 pokud trojice není, jinak je na výstupu znak ze kterého je trojice. Pokud je více trojic, vybere
    první, na kterou narazí
    '''
    for i in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
        a = tabulka[i[0]]
        if a != 0 and a == tabulka[i[1]] and a == tabulka[i[2]]:
            return a
    return 0        
def dva(tabulka:list[int])->list:
    '''
    Funkce, která počítá rozdíl mezi počtem otevřených dvojic (tj. dvojic stejného nenulového znaku v řadě, sloupci či diagonále
    u kterých je třetí znak je nula takže tato dvojice je doplnitelná na trojici) dvou hráčů.
    tabulka: seznam délky 81 obsahující pouze prvky 0, 1 a -1. reprezentuje herní pozici, pro kterou chceme tento rozdíl zjistit
    Na výstupu je seznam délky 9 obsahující množiny, které jsou podmnožinou množiny {-1,1}
    '''
    vystup = [set(),set(),set(),set(),set(),set(),set(),set(),set()]
    for i in range(9):
        for k in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
            co_kontrolujeme = [tabulka[9*i+k[0]],tabulka[9*i+k[1]],tabulka[9*i+k[2]]]
            if co_kontrolujeme.count(0) == 1:
                if co_kontrolujeme.count(1) == 2:
                    vystup[i].update([1])
                elif co_kontrolujeme.count(-1) == 2:
                    vystup[i].update([-1])
    return(vystup)
def ohodnot(tabulka:list) -> int:
    '''
    Funkce, která kombinuje funkce dva() a tri(). Tedy přiřadí pozici číslo dle toho kdo a jak moc má navrch. 
    tabulka: seznam délky 81 obsahující pouze prvky 0, 1 a -1. Reprezentuje pozici, kterou chceme ohodnotit
    Na výstupu je číslo mezi -10 a 10.
    '''
    for i in range(9):
        a = tri(tabulka[9*i:9*(i+1)])
        if a != 0:
            return a*10
    a = dva(tabulka)
    soucet = 0
    for i in a:
        if 1 in i:
            soucet +=1
        if -1 in i:
            soucet -=1
    return soucet
def negamax(pozice:Uzel):
    '''
    Funkce, která ze stromu s ohodnocenými uzly vybere nejlepší cestu pomocí varianty algorytmu minmax tzv. negamaxu.
    pozice: Uzel představující pozici od které chceme prohledávat
    Na výstupu je dvojprvkový seznam obsahující seznam políček (čísel), které vedou k nejlepší situaci při perfektní hře a druhým
    prvkem je ohodnocení této nejlepší pozice
    '''
    if not pozice.moznosti:
        return [[], ohodnot(pozice.data)]
    dalsi = [negamax(mozne) for mozne in pozice.moznosti]
    nejlepsi = pozice.hrac * max(pozice.hrac * c[1] for c in dalsi)
    kde_nejlepsi = [pozice.moznosti[i].posledni for i in range(len(pozice.moznosti)) if dalsi[i][1] == nejlepsi]
    return [kde_nejlepsi, nejlepsi]
pygame.init()
kontrola_komb = {}
screen = pygame.display.set_mode((1024, 512))
clock = pygame.time.Clock()
running = prvni = True
clicking = False
tah = -1
x,y = 1024, 512#screen.get_size()
grid_nastiveno = [0]*81
barvy = [(255,0,0),(0,255,0),(0,0,255)]
aktivni = random.choice([-1,1])
done = False
a,b = [(x*i)//4 for i in [1,2,3]], [(y*i)//4 for i in [1,2,3]]
moznosti = [-30,-10,10]
grid = [[a_+k,b_+i,20,20] for b_ in b for a_ in a for i in moznosti for k in moznosti]
screen.fill((155,0,0))
for  a_ in a:
    for b_ in b:
        pygame.draw.rect(screen,(255,255,255),[a_-30,b_-30,60,60],0)
for i in grid:
    pygame.draw.rect(screen,(0,0,0),i,1)
while running:
    mx,my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                clicking = True
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                clicking = False
    if aktivni == 1:
        for a_cis,a_ in enumerate(a):
            for b_cis,b_ in enumerate(b):
                if clicking and abs(mx-a_)<30 and abs(my-b_)<30 and not done and (prvni or (a_cis == (tah % 9)%3 and b_cis == (tah % 9)//3)):
                    pos = 27*(b_cis) + 9*(a_cis) + ((mx-a_+30)//20)+3*((my-b_+30)//20)
                    prvni = False
                    if grid_nastiveno[pos]==0:
                        for i in grid:
                            pygame.draw.rect(screen,(0,0,0),i,1)
                        pygame.draw.rect(screen,barvy[aktivni],grid[pos],0)
                        grid_nastiveno[pos] = aktivni

                        vyherni = tri(grid_nastiveno[27*(b_cis) + 9*(a_cis):27*(b_cis) + 9*(a_cis)+9])
                        if vyherni != 0:
                            done = True
                            screen.fill(barvy[vyherni])
                        if 0 not in grid_nastiveno:
                            done = True
                            screen.fill(barvy[0])
                        aktivni *= -1
    if aktivni == -1 and not done:
        if prvni:
            prvni = False
            tah = random.randint(0,80)
            grid_nastiveno[tah] = -1
            pygame.draw.rect(screen,barvy[-1],grid[tah],0)
            aktivni *= -1
            for i in range(9):
                pygame.draw.rect(screen,(255,255,0),grid[9*(tah%9)+i],1)
            continue
        hledani_moznosti(grid_nastiveno,pos)
        nega,check = negamax(kontrola_komb[tuple(grid_nastiveno)])
        tah = nega[random.randint(0,len(nega)-1)]
        grid_nastiveno[tah] = -1
        pygame.draw.rect(screen,barvy[-1],grid[tah],0)
        for i in range(9):
            pygame.draw.rect(screen,(255,255,0),grid[9*(tah%9)+i],1)
        vyherni = kontrola_komb[tuple(grid_nastiveno)].hodnota
        if vyherni != 0:
            done = True
            screen.fill(barvy[vyherni])
        if 0 not in grid_nastiveno:
            done = True
            screen.fill(barvy[0])
        aktivni *= -1
    pygame.display.flip()
    clock.tick(60)
pygame.quit()