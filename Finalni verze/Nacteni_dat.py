import datetime
from bs4 import BeautifulSoup
from os import walk
import xlrd
import os, pickle
from dateutil.parser import parse

#Zde načítám všechny potřebné knihovny

Dir='Data\\'    #Určení místa kde budou datové soubory vzhledem k hlavnímu programu

#-----------------------Začátek načtení dat z danného rozvrhu jedné třídy----------------------
"""Tyto funkce mají za účel získat data z nahraného rozvrhu hodin.
Jedná se přímo o rozvrh dané třídy, stažený ze školních webových stránek"""


def Get_Subjects(File):         #Tato funkce vrací všechny předměty které žák ve škole absolvuje
    with open(Dir+File,encoding='utf8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        subjects=[]
        for i in range(1,6):
            for j in range(0,9):
                try:
                    if soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[0]['class'][0]=='lesson1':
                        if soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("span", class_="subject").text not in subjects:
                            subjects.append(soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("span", class_="subject").text)
                    else:
                        for k in range(int(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[0]['class'][0].replace('lesson',''))):
                            if soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("span", class_="subject").text not in subjects:
                                subjects.append(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("span", class_="subject").text)
                except:
                    pass
    return subjects

def Get_Days(File):     #Získá údaje o rozvrhu z jednoho html souboru
    with open(Dir+File,encoding='utf8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        names=[]
        days=[]

        body=soup.tbody.find_all("tr")
        for i in range(1,6):
            names.append(body[i].th.text)
            List=[]
            for j in range(0,9):
                try:
                    List2=[]
                    if soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[0]['class'][0]=='lesson1':
                        List3 = []
                        List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("a", class_="room").text)
                        List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("a", class_="employee").text)
                        List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("span", class_="subject").text)
                        List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].div.find("span", class_="class").text)
                        List2.append(List3)
                    else:
                        for k in range(int(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[0]['class'][0].replace('lesson',''))):
                            List3=[]
                            List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("a", class_="room").text)
                            List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("a", class_="employee").text)
                            List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("span", class_="subject").text)
                            List3.append(soup.tbody.find_all("tr")[i].find_all('td')[j].find_all('div')[k].find("span", class_="class").text)
                            List2.append(List3)


                except:
                    List2=[4*[None]]
                List.append(List2)
            days.append(List)
    return tuple(days)


#-----------------------Začátek načtení dat z rozvrhů místností školy--------------------------
"""Tato část kódu je určena spíše do budoucna pro možnost získávat rozvrhy daných tříd 
ze předepsaných rozvrhů místností a učeben na škole

V tuto chvíli není v programu využíván"""


class Trida:        #Objekt, který pracuje s daty o jedné třídě a zachovává údaje o ní
    def __init__(self,Name):
        self.Class_Name=Name
        self.Class_Teacher=None
        self.Class_Room=None
        self.Class_Table=[]
        self.DefTable()

    def DefTable(self):
        for i in range(0,5):
            list=[]
            for j in range(0,9):
                list.append([4*[None]])
            self.Class_Table.append(list)

    def SetTable(self,Day, Hour, Room):
        self.Class_Table[Day][Hour]=Room

    def AppendTable(self,Day, Hour, Room):
        self.Class_Table[Day][Hour].append(Room)

def FindClass(Object,Name):     #Vrátí index v objektu dle jména
    for Class in Object:
        if Class.Class_Name==Name:
            return Object.index(Class)
    return None

def LoadTable(Class):
    f = []
    for (dirpath, dirnames, filenames) in walk(Dir+'Rozvrhy_mistnosti\\'):
        f.extend(filenames)
        break


    Classes=[]
    Classes_Names=[]


    for file in f:
        room=Get_Days('Rozvrhy_mistnosti\\'+file)
        for day in range(len(room)):
            for hour in range(len(room[day])):
                if room[day][hour][0] is not [4*[None]]:
                    Classes_Names.append(room[day][hour][0][3])
                    if FindClass(Classes,room[day][hour][0][3]) is not None:
                        if Classes[FindClass(Classes,room[day][hour][0][3])].Class_Table[day][hour] is None:
                            Classes[FindClass(Classes,room[day][hour][0][3])].SetTable(day,hour,room[day][hour])
                        else:
                            Classes[FindClass(Classes, room[day][hour][0][3])].SetTable(day, hour, room[day][hour])
                    else:
                        CLS=Trida(room[day][hour][0][3])
                        CLS.SetTable(day,hour,room[day][hour])
                        Classes.append(CLS)


    for item in Classes:
        if item.Class_Name==Class.lower().capitalize():
            return item.Class_Table
    return None


#-----------------------Začátek načtení dat ze suplování z xlsx souboru------------------------
"""Funkcí následující části je získat data ze souboru suplování, který je stažen ze školních stránek z online excel tabulky"""


class Trida2:       #Jiny objekt pro uchovani dat o jedne tride a jejim nahradnim rozvrhu suplovani
    def __init__(self, name,Teacher,Room, supl):
        self.name = name
        self.Teacher = Teacher
        self.Room = Room
        self.supl = supl

class Den:          #Objekt pro  uchovani jedne tridy a dne v jakem se o rozvrh jedna
    def __init__(self, name, tridy):
        self.name = name
        self.tridy = tridy

def Get_Supl(File):     #Vrací přímo list všech dní a změn pro každou třídu
    workbook = xlrd.open_workbook(Dir+File)

    Days=[]
    for i in range(len(workbook.sheets())):
        worksheet = workbook.sheet_by_index(i)
        try:
            yx_start=None
            yx_start_dist = None



            for x in range(worksheet.ncols):
                for y in range(worksheet.nrows):
                    if worksheet.cell_value(y, x)=="\numístění":
                        if yx_start==None:
                            yx_start=(y,x)
                        elif yx_start is not None:
                            yx_start_dist=(y,x)

            if worksheet.cell_value(yx_start[0]-2,yx_start[1]).strip()!='':
                Name=worksheet.cell_value(yx_start[0]-2,yx_start[1]).strip()
            else:
                Name = worksheet.cell_value(yx_start[0] - 3, yx_start[1]).strip()


            Tridy = []
            for y in range(1,22):
                Class=(worksheet.cell_value(y + int(yx_start[0]), int(yx_start[1])))
                Class_Name=Class.split('/')[0]
                Class_Teacher=Class.split('\n')[0].split('/')[1]
                Class_Room=Class.split('\n')[1]
                List=[]
                for x in range(1,10):
                    List.append(str(worksheet.cell_value(y + int(yx_start[0]), x+int(yx_start[1]))).replace('\n',' '))
                Tridy.append(Trida2(Class_Name,Class_Teacher,Class_Room,List))

            Days.append(Den(Name,Tridy))


        except:
            pass

    return Days

def Get_This_Week(Class):       #Načte data ze suplování na následující týden
    Supl = Get_Supl('Suplování.xlsx')
    List = []
    for day in Supl:
        for trida in day.tridy:
            if trida.name == Class:
                dayx = day.name.lower()
                dayx = dayx.replace('á', 'a')
                dayx = dayx.replace('í', 'i')
                dayx = dayx.replace('  ', ' ')
                dayx = dayx.replace('. ', '.')
                dayx = dayx.replace('.  ', '.')
                if not dayx == '':
                    matches = parse(dayx, fuzzy=True, dayfirst=True)
                else:
                    matches = 'None'
                List.append([matches, trida.supl])

    Days=[]
    Data=[]

    for day in List:
        if day[0] is not str and day[0] is not "None":
            if day[0].date() > datetime.datetime.now().date():
                if day[0].date() < datetime.timedelta(days=7)+datetime.datetime.now().date():
                    Days.append(day[0].strftime('%w'))
                    Data.append(day[1])
    return Days,Data



#-----------------------Začátek načtení dat rozvrhů a aktualizace------------------------------


def Actual_Timetable():     #Načte přímo aktuální rozvrh hodin, a upraví ho na následující týden dle dat získaných ze suplování
    Timetable=list(Get_Days('Urcity rozvrh hodin.html'))
    for Day in Timetable:
        for Hour in Day:
            for Part in Hour:
                if Part[3] is not None:
                    Class=Part[3]
                    break
    Days,Data=Get_This_Week(Class)
    for index,day in enumerate(Days):
        Days[index]=str(int(day)-1)


    for index1,day in enumerate(Days):
        for index,hour in enumerate(Timetable[int(day)]):
            if Data[index1][index]!='':
                Timetable[int(day)][index]=[[None,None,Data[int(index1)][index],None]]

    return Timetable



#-----------------------Začátek načtení dat domácích úkolů-------------------------------------
"""Zde už program pracuje přímo s daty o domácích úkolech"""

Filename='Ukoly'

class Ukol:     #Tento objekt má za účel uchovávat informace potřebné ke každému úkolu
    def __init__(self):
        self.Start_date=None
        self.Start_Place=None
        self.End_date=None
        self.End_Place = None
        self.Subject = None
        self.Title = None
        self.Description = None
        self.Optianoly = None
        self.Status = None

def CreateFile(Object):     #Uloží aktualizaci úkolů a případně založí soubor potřebný k uložení
    if not os.path.exists(Filename):
        open(Filename,'x')

    with open(Filename, 'wb') as f:
        pickle.dump(Object, f)

def LoadData():         #Načte data ze souboru s uloženými úkoly
    if not os.path.exists(Filename):
        open(Filename,'x')
    if os.path.getsize(Filename) > 0:
        with open(Filename, 'rb') as inp:
            List=pickle.load(inp)

        return List
    return None





#-----------------------Začátek testovacího kódu pro spuštění funkcí programu------------------
"""Tato část slouží k případné nutnosti program dubugovat při budoucích úpravách"""
#Days=Get_Days('Data\\Urcity rozvrh hodin.html')
#Table=LoadTable('Data\\Rozvrhy_mistnosti\\','A4')
#Suplovani=Get_Supl('Data\\Suplování.xlsx')
#New=Actual_Timetable()
