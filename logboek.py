import re
from datetime import datetime

def parse_log_entry(line):
    """Parse a log entry line into a dictionary."""
    parts = line.split('\t')
    if len(parts) < 9:
      return None  # Skip incomplete lines
    
    entry = {
        'datum': parts[0].strip(),
        'uren_joost': parts[1].strip() if parts[1].strip() else '0',
        'uren_jonathan': parts[2].strip() if parts[2].strip() else '0',
        'joost_bool': parts[3].strip(),
        'jonathan_bool': parts[4].strip(),
        'joost_wat': parts[5].strip(),
        'jonathan_wat': parts[6].strip(),
        'plaats': parts[7].strip(),
        'afspraken': parts[8].strip() if len(parts) > 8 else '',
        'overig': parts[9].strip() if len(parts) > 9 else ''
    }
    
    return entry


def filter_empty_days(entries):
    """Filter out days where nothing happened."""
    filtered_entries = []
    for entry in entries:
        if (entry['joost_bool'].upper() == 'TRUE' or entry['jonathan_bool'].upper() == 'TRUE' 
            or entry['uren_joost'] != '0' or entry['uren_jonathan'] != '0'
            or entry['joost_wat'] != '' or entry['jonathan_wat'] != ''
            or entry['afspraken'] != '' or entry['overig'] != ''):
            filtered_entries.append(entry)
    return filtered_entries

def format_for_latex(entries):
    """Format the log entries for LaTeX longtable."""
    
    latex_lines = [
        r"\begin{longtable}{@{}p{2cm} p{1.5cm} p{1.5cm} p{6cm} p{6cm}}",
        r"\toprule",
        r"Datum  & Uren Joost & Uren Jonathan & Joost wat is er gedaan? & Jonathan wat is er gedaan? & Overig \\",
        r"\hline",
        r"\midrule",
        r"\endhead",
    ]

    total_uren_joost = 0.0
    total_uren_jonathan = 0.0
    total_joost_count = 0
    total_jonathan_count = 0
    
    for entry in entries:
        # Convert date to day of the week in dutch
        try:
            date_obj = datetime.strptime(entry['datum'].split(' ')[0], '%d/%m/%y')
            day_of_week = date_obj.strftime('%a')
            dutch_days = {
                'Mon': 'ma',
                'Tue': 'di',
                'Wed': 'wo',
                'Thu': 'do',
                'Fri': 'vr',
                'Sat': 'za',
                'Sun': 'zo'
            }
            day_of_week_dutch = dutch_days.get(day_of_week)
        except ValueError:
            day_of_week_dutch = entry['dag']
                
        try:
            uren_joost = float(entry['uren_joost'])
        except ValueError:
            uren_joost = 0.0

        try:
            uren_jonathan = float(entry['uren_jonathan'])
        except ValueError:
            uren_jonathan = 0.0
        
        if uren_joost == 0 and uren_jonathan == 0:
            continue
          
            
        total_uren_joost += uren_joost
        total_uren_jonathan += uren_jonathan
        
        if entry['joost_bool'].upper() == 'TRUE':
            total_joost_count += 1
        elif entry['joost_bool'].upper() != 'FALSE':
            total_joost_count +=1
        if entry['jonathan_bool'].upper() == 'TRUE':
            total_jonathan_count += 1
        elif entry['jonathan_bool'].upper() != 'FALSE':
            total_jonathan_count +=1
        
        
        # Escape latex special characters
        joost_wat = entry['joost_wat'].replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}').replace('\n', ' ')
        jonathan_wat = entry['jonathan_wat'].replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}').replace('\n', ' ')
        overig = entry['overig'].replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}').replace('\n', ' ')

        latex_line = f"{entry['datum'].split(' ')[0]} {day_of_week_dutch} & {uren_joost} & {uren_jonathan} & {joost_wat} & {jonathan_wat} \\\\"
        latex_lines.append(latex_line)
    
    # Add totals row
    latex_lines.append(r"\midrule")
    latex_lines.append(f"Totalen & & {total_uren_joost:.1f} & {total_uren_jonathan:.1f} & & & \\\\")
    latex_lines.append(r"\bottomrule")
    latex_lines.append(r"\end{longtable}")
    
    return "\n".join(latex_lines)


def main():
    log_text = """
Logboek Joost & Jonathan Fase 4
dag	Uren Joost	Uren Jonathan	Joost	Jonathan	Joost wat is er gedaan?	Jonathan wat is er gedaan?	plaats	Afspraken op deze datum	Overig
Totalen	86	84	48	34					
09/10/24  Wed		3	FALSE	TRUE		Toets nakijker Verttouwen toegevoegd			
14/10/24  Mon	1	3	TRUE	TRUE	analyseren secties toevoegen	Aan de toetsen gewerkt			
15/10/24  Tue	1	3	TRUE	TRUE	"met Mevr. Vos besproken wat zij verwacht van een analyse site
met Jonathan overlegd over de scheikunde toets"	Aan de enquête gewerkt			
16/10/24  Wed	0.5		TRUE	FALSE	mini onderzoek enquete opgesteld: incl. vraag, methode, hypothese enz				
17/10/24  Thu	1	0.5	TRUE	TRUE	"enquete door mr koch laten bekijken en enquete verstuurd, 
gestart individuele item stats in analyse site"	Aan de enquête gewerkt + gestuurd			
18/10/24  Fri			TRUE	FALSE					
19/10/24  Sat	0.5		TRUE	FALSE	normaalverdelingen toegevoegd aan de analyse site				
20/10/24  Sun			FALSE	FALSE					
21/10/24  Mon		2	FALSE	TRUE		Forced JSON			
22/10/24  Tue			FALSE	TRUE		Getst met visuele inpots			
23/10/24  Wed			FALSE	FALSE					
24/10/24  Thu			FALSE	FALSE					
25/10/24  Fri			FALSE	FALSE					
26/10/24  Sat			FALSE	FALSE					
27/10/24  Sun		3	FALSE	TRUE		Temperaturen getsest			
28/10/24  Mon			FALSE	FALSE					
29/10/24  Tue			FALSE	FALSE					
30/10/24  Wed			FALSE	FALSE					
31/10/24  Thu		2	FALSE	TRUE		Prompts getest			
01/11/24  Fri			FALSE	FALSE					
02/11/24  Sat	1		TRUE	FALSE	toetsblaadje pdf afgemaakt				
03/11/24  Sun			FALSE	FALSE					
04/11/24  Mon			FALSE	FALSE					
05/11/24  Tue			FALSE	FALSE					
06/11/24  Wed			FALSE	FALSE					
07/11/24  Thu	2		TRUE	FALSE	google cloud function voor de inscanner				
08/11/24  Fri	3		TRUE	FALSE	afmaken functions docker containerizing				
09/11/24  Sat	2		TRUE	FALSE	website en opnieuw proberen te containen				
10/11/24  Sun			FALSE	FALSE					
11/11/24  Mon	1		FALSE	FALSE	qr code creator in iupyter notebook gemaakt				
12/11/24  Tue	1		TRUE	FALSE	omgezet naar de api en toegevoegd aan de vuejs site				
13/11/24  Wed		2	FALSE	TRUE		Implementatie Gemini			
14/11/24  Thu			FALSE	FALSE					
15/11/24  Fri			FALSE	FALSE					
16/11/24  Sat			FALSE	FALSE					
17/11/24  Sun		2	FALSE	TRUE		Gemini met afbeeldingen			
18/11/24  Mon			FALSE	FALSE					
19/11/24  Tue			FALSE	FALSE					
20/11/24  Wed			FALSE	FALSE					
21/11/24  Thu			FALSE	FALSE					
22/11/24  Fri	1		TRUE	FALSE	api route toegevoegd die alles kan				
23/11/24  Sat		2	FALSE	TRUE		Begonnen met implementatie klassengemiddelden			
24/11/24  Sun			FALSE	FALSE					
25/11/24  Mon	1		TRUE	FALSE	api route die alles kan geintegreert in ui. bugs in square detector gefixed				
26/11/24  Tue			FALSE	FALSE					
27/11/24  Wed			FALSE	FALSE					
28/11/24  Thu			FALSE	FALSE					
29/11/24  Fri	2.5	4	TRUE	TRUE	"gesprek met hermarij over progressie en toetsje 3e klas
verder gegaan met inscan onderzoek (2500 * 5 api requests)"	Asynchrone requests	school en thuis	toetsje 3e klas afmaken	
30/11/24  Sat	1		TRUE	FALSE	enquete resultaten on tabellen zetten				
01/12/24  Sun	1		TRUE	FALSE	inscan onderzoek resultaten in tabellen zetten				
02/12/24  Mon			FALSE	FALSE					
03/12/24  Tue			FALSE	FALSE					
04/12/24  Wed	2.5	1.5	TRUE	TRUE	methode inscannen	Toets gemaakt			
05/12/24  Thu			FALSE	FALSE					
06/12/24  Fri	1		TRUE	FALSE	verder met methode inscannen				
07/12/24  Sat	3		TRUE	FALSE	methode inscannen afgerond en gestart methode analyseren				
08/12/24  Sun			FALSE	FALSE					
09/12/24  Mon		1.5	FALSE	TRUE		Rubric aangepast			
10/12/24  Tue	2		TRUE	FALSE	resultaten tabellen inscannen				
11/12/24  Wed	2		TRUE	FALSE	latex package bug fixen en verder met tabellen				
12/12/24  Thu	1		TRUE	FALSE	in mediatheek gemini 2.0 flash testen				
13/12/24  Fri	3	2	TRUE	TRUE	toets gegeven 3e klas eerste nakijktest	toets gegeven 3e klas 			
14/12/24  Sat	1	1.5	TRUE	TRUE	conclusie geschreven inscannen en analyseren	Handmatig toets nagekeken			
15/12/24  Sun	1.5		TRUE	FALSE	tests met inscansite				
16/12/24  Mon	1		TRUE	FALSE	foutanalyse mijn onderdelen + vervolgonderzoek + opzet samenvatting onderzoek				
17/12/24  Tue		5	FALSE	TRUE		Toets met 6 modellen nagekeken			
18/12/24  Wed	2	3.5	TRUE	TRUE	nakijk resultaten geformateerd + uitleg instellen latex vscode	nakijk methode geschreven			
19/12/24  Thu	2	4.5	TRUE	TRUE	afmaken document + conclusie schrijven				
20/12/24  Fri			TRUE	TRUE	inleveren	inleveren			
21/12/24  Sat			FALSE	FALSE					
"""
    log_text = """
    Logboek Joost & Jonathan Fase 3									
dag	Uren Joost	Uren Jonathan	Joost	Jonathan	Joost wat is er gedaan?	Jonathan wat is er gedaan?	plaats	Afspraken op deze datum	Overig
Totalen	43.5	38	19	15					
16/06/24  Sun		2	FALSE	TRUE		Proef LLM model gemaakt m.b.v. PyReft	Thuis		
21/06/24  Fri		2	TRUE	FALSE		Toetsdata geanonimiseerd 	School		Met meneer Hermarij
09/09/24  Mon	1		TRUE	FALSE	Gestart met brief aan Studente				
14/09/24  Sat	2		TRUE		PDF -> image, rode pen weggehaald (dmv python), gestart met het opsplitsen van antwoorden in secties				
19/09/24  Thu	1		TRUE	FALSE	Joost gesprek met begeleider		school		
21/09/24  Sat	4		TRUE	FALSE	gestart gebruikt handbook en eerste secties onderscheiden. logboek 				
28/09/24  Sat	1.5	3	TRUE	TRUE	Joost correctie toegeveogd voor foute opdrachtnummer herkenning ('b' -> 6)	Begin met website voor toetsen analyseren. Start gemaakt met de routing en templates voor de website.	Thuis		
29/09/24  Sun	5	4	TRUE	TRUE	"zo veel mogelijk tekst herkennings modellen getest op verschilldende soorten antwoorden
python jupiter notebook gebruikt voor automatiseren van foto verandering"	Verder gegaan met de website. Routing en index-template afgemaakt.	Thuis		
30/09/24  Mon	5.5	4.5	TRUE	TRUE	"3 tussenuren heb fase 3 bestand opgemaakt en start uitwerking deelvragen
gpt api gekoppeld aan python script voor tekstherkenning
toets analyse app features/doelen/logboek uitgewerkt"	Start gemaakt aan deelvraag toetsantwoorden nakijken. Programma geschreven om ingescande data te formateren. Start gemaakt aan programma om API-requests naar openAI te sturen.	Thuis		
01/10/24  Tue		2	FALSE	TRUE		Verder gegaan met programma voor de openAI API-requests.			
02/10/24  Wed	2	4	TRUE	TRUE	"wireframe voor de analyze website zodat we weten welke data en functies er nodig zijn
classes in de analyze website toegevoegd
"	Onderzoek gedaan naar de API en verdergegaan met het programma			
03/10/24  Thu	1.5		TRUE	FALSE	Fase 3 bestand opmaken, correlatie en covariatie toegevoegd aan de classes				
04/10/24  Fri			FALSE	FALSE					
05/10/24  Sat	2	3	FALSE	TRUE	vuejs test site gemaakt, contact met daniel markus	Legacy output geherstructureerd			
06/10/24  Sun	2		TRUE	FALSE	fase 3 2 bronnen toegevoegd, nieuwe output indeling inscan modules. nieuwe tabel in analyseren				
07/10/24  Mon			FALSE	FALSE					
08/10/24  Tue	7.5	4	TRUE	TRUE	"gesprek met Daniel Marcus bij LevelUp en daaruit doelen gehaald. 
Nieuwe proefwerkblaadjes om makkelijk in te scannen en notebook voor geschreven"	Basis programma gemaakt			
    """
    log_text =  """
Logboek Joost & Jonathan Fase 2									
dag	Uren Joost	Uren Jonathan	Joost	Jonathan	Joost wat is er gedaan?	Jonathan wat is er gedaan?	Plaats	Afspraken op deze datum	Overig
Totalen	8.5	9.5	8	7					
18/03/24	0.5	0.5	TRUE	TRUE	Begin aan de motivatiebrief; de opzet en samenwerking	Begin aan de motivatiebrief; de opzet en samenwerking.	thuis		
19/03/24	1.5	1.5	TRUE	TRUE	Afschrijven van de motivatiebrief	Afschrijven van de motivatiebrief.	thuis		
08/05/24	0.5	0	TRUE	FALSE	filmpje NOS en format fase 2 		thuis		
13/05/24	1	0	TRUE	FALSE	Layout fase 2 document en  literatuurondezoek		thuis		
14/05/24	0	2.5	FALSE	TRUE		Drie studies uitgekozen en samengevat.	thuis		
15/05/24	1	1	TRUE	TRUE	Voorbereiden op gesprek begeleider.	Voorbereiden op gesprek begeleider.	school	Er moet een proefje gedaan worden.	
28/05/24	1	0	TRUE	FALSE	Eén studie samengevat.				
03/06/24	1.5	0	TRUE	FALSE	De planning van fase 2 en 3 gemaakt.		thuis		
06/06/24	0.5	0	TRUE	FALSE	Samenvatting An automatic short-answer grading model for semi-open-ended questions		thuis		
04/06/24	0	1	FALSE	TRUE		Onderzoek gedaan naar Finetuning van LLMs	school		
06/06/24	0	1.5	FALSE	TRUE		Onderzoek gedaan  naar REFT, PYREFT & LORA.	school		
10/06/24	1	1.5	FALSE	TRUE	Puntjes op de i fase 2 en ingeleverd	Logboek en eisenlijst verbeterd; puntjes op de i fase 2	thuis		
    """

    log_lines = log_text.strip().split('\n')[3:]
    log_entries = [parse_log_entry(line) for line in log_lines if parse_log_entry(line) is not None]

    # Sort by date (most recent first)
    def date_sort_key(entry):
      try:
        return datetime.strptime(entry['datum'], '%d/%m/%y')
      except ValueError:
        return datetime.min #put dates at the bottom that can't be parsed
    
    log_entries.sort(key=date_sort_key, reverse=True)
    
    filtered_entries = filter_empty_days(log_entries)
    latex_output = format_for_latex(filtered_entries)
    print(latex_output)

if __name__ == "__main__":
    main()