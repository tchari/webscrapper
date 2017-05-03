#The purpose of this script is to mine DnD 5e spell information. The complete
#list of spells must be generated and stored in the spell_list.txt file.
#This script reads the html files from dnd-spells.com, parses the relevant,
#spell information, and saves is to a semi-colon delimited CSV file.
#Some html files will through errors in this script due to odd characters. 
#These spells are saved in the ERROR_list and can be parsed by hand (< 10 spells).

from bs4 import BeautifulSoup
import urllib.request

school_list = ['Abjuration', 'Conjuration', 'Divination', 'Enchantment', 'Evocation', 'Illusion', 'Necromancy', 'Transmutation']
screwy_chars = ["\x82","\x84","\x85","\x88","\x91","\x92","\x93","\x94","\x95","\x96","\x97","\x99","\n","\r"]
EOL = "\n"
URL_prefix = 'http://www.dnd-spells.com/spell/'
Spell_info_file = open('spell_details.csv', 'w')

Spell_list_file = open('spell_list.txt','r')
spell_list = Spell_list_file.read().splitlines()
Spell_list_file.close()

ERROR_list = []

for name in spell_list:
    try:
        URL = URL_prefix+name
        print("Accessing URL: " + URL)
        bytesURL = urllib.request.urlopen(URL).read()
        print("Parsing text")
        soup = BeautifulSoup(bytesURL.decode(errors='ignore'), 'lxml')
        paragraphs = list(soup.find_all('p')) #important data is stored in <p>

        for i in enumerate(paragraphs):
            if paragraphs[i[0]].get_text() in school_list:
                break
        index = i[0] #index is the <p> that begins the useful data to mine

        school = paragraphs[index].get_text()
        index = index+1
        while len(paragraphs[index])<2: #skip empty or nearly empty <p>
            index = index+1

        LCRCD = paragraphs[index].get_text() #This <p> contains Level, Casting time, Range, Components, Duration information
        i = 0
        while i<len(LCRCD):
            if LCRCD[i:i+6] == 'Level:': #level attribute
                start_ind = i+6 #jump to caracters after "Level :"
                i = start_ind
                while LCRCD[i] != EOL:
                    i=i+1
                level = LCRCD[start_ind:i] #mine level characters
                level = level.strip()
            elif LCRCD[i:i+13] == 'Casting time:': #Casting time attribute
                start_ind = i+13
                i = start_ind
                while LCRCD[i] != EOL:
                    i=i+1
                casting_time = LCRCD[start_ind:i] #mine casting time characters
                casting_time = casting_time.strip()
            elif LCRCD[i:i+6] == 'Range:': #Range attribute
                start_ind = i+6
                i = start_ind
                while LCRCD[i] != EOL:
                    i=i+1
                cast_range = LCRCD[start_ind:i] #mine casting range characters
                cast_range = cast_range.strip() 
            elif LCRCD[i:i+11] == 'Components:': #Range attribute
                start_ind = i+11
                i = start_ind
                while LCRCD[i] != EOL:
                    i=i+1
                components = LCRCD[start_ind:i] #mine component requirements
                components = components.strip()
            elif LCRCD[i:i+9] == 'Duration:': #Range attribute
                start_ind = i+9
                i = start_ind
                while LCRCD[i] != EOL:
                    i=i+1
                duration = LCRCD[start_ind:i] #mine duration characters
                duration = duration.strip()
            else:
                i=i+1 #Scan through until one of the above cases is true

        index = index+1 #move on to the next <p>            
        while len(paragraphs[index].get_text())<2: #skip empty or nearly empty <p>'s
            index = index+1

        #spell list descriptions could be in multiple <p>'s. Mine each one until
        #we get to the Page # <p> block and then stop.
        spell_desc_list = []
        flag = 0 #Flag to indicate Page <p> block
        while not flag:
            text = paragraphs[index].get_text()
            if "Page" and ("Players Handbook" or "Elemental Evil" or "Sword Coast Adventurer's Guide")in text: #Page <p> block
                flag = 1
                break
            spell_desc_list.append(paragraphs[index].get_text().strip())
            index = index+1

        #Discern which manual the spell comes from using Test
        test = paragraphs[index].get_text().strip()
        page = ''
        if test[0:5] == 'Page:':
            if test[len(test)-16:len(test)] == 'Players Handbook':
                dignum = 1	#tracks the number of digits in the page number
                ind_num_start = 6 #6 = character position after 'Page: '
                i = ind_num_start
                while test[i] in ['0','1','2','3','4','5','6','7','8','9']:
                    dignum = dignum+1
                    i=i+1
                page = test[ind_num_start:i] + ' PHB'
            elif test[len(test)-14:len(test)] == 'Elemental Evil':
                dignum = 1
                ind_num_start = 6
                i = ind_num_start
                while test[i] in ['0','1','2','3','4','5','6','7','8','9']:
                    dignum = dignum+1
                    i=i+1
                page = test[ind_num_start:i] + ' EE'
            elif test[len(test)-29:len(test)] == "Sword Coast Adventure's Guide":
                dignum = 1
                ind_num_start = 6
                i = ind_num_start
                while test[i] in ['0','1','2','3','4','5','6','7','8','9']:
                    dignum = dignum+1
                    i=i+1
                page = test[ind_num_start:i] + ' SCAG'
            else:
                print('Unknown page/source')
                page = 'XXX'
        
        
        spell = [name, level, casting_time, cast_range, components, duration, page, spell_desc_list]
        temp = ''
        for items in spell_desc_list: #spell_desc_list is a list of paragraphs containing the spell descriptions: turn this into one string.
            temp = temp + items
        for chars in screwy_chars: #replace unrepresentable ASCII characters with nothing
            temp = temp.replace(chars, '')
        spell_description = temp
        output_string = name + ';' + level + ';' + casting_time + ';' + cast_range + ';' + components + ';' + duration + ';' + page + ';' + spell_description + '\n'
        Spell_info_file.write(output_string)        
        print("Finished " + name)
        print("\n\r")
    except UnicodeError as err:
        ERROR_list.append(name)
        print("Unicode error on spells: " + name + "\n")
        print(err)
    except Exception as e:
        ERROR_list.append(name)
        print("Generic error on spell: " + name + "\n")
        print(e)
        print("\n")
        print("Unexpected error:", sys.exc_info()[0])
        
Spell_info_file.close()
