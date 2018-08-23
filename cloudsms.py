import json, urllib.parse, urllib.request
import re
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import random
from io import BytesIO
from PIL import Image
#Redact the keys if publishing anywhere public pls.
account_sidtrial = "REDAC"
auth_tokentrial = "REDAC"
account_sid = "REDAC"
auth_token = "REDAC"
phonetrial = "+12262429729"
phone = "+12262429729"
from newsapi import NewsApiClient




#Redact the API key if publishing anywhere public pls
newsapi = NewsApiClient(api_key='REDAC')
'''
Apologies for the code that's messy everywhere! This was made during a hackathon and thus it's hacky code :) (Working, hacky code)
'''



phoneinuse = phone
account_sidinuse = account_sid
auth_tokeninuse = auth_token
def has(parsedjson,identifier):
    try:
        for x in range(100):
            if str(identifier) in str(parsedjson['queryresult']['pods'][x]['title']):
                return True
        return False
    except:
        return False
def find(parsedjson,identifier):
    try:
        decisor = 100
        for x in range(100):
#            print(str(parsedjson['queryresult']['pods'][x]['title']))
            if str(identifier) in str(parsedjson['queryresult']['pods'][x]['title']):
                decisor = x
                break
        returnstring = str(parsedjson['queryresult']['pods'][decisor]['subpods'][0])
        returnstring = stripBasic(returnstring)
        return returnstring
    except Exception as e:
        return ""


def getLocations(input):
    textlist = input.lower().split(" ")
    finalindex = 0
    mode = "driving"
    if (textlist[1] == "to"):
        finalindex = 0
        toindex = 0
        fromindex = 0
        try:
            finalindex = textlist.index("walking")
            mode = "walking"
        except:
            try:
                finalindex = textlist.index("driving")
                mode = "driving"
            except:
                try:
                    finalindex = textlist.index("transit")
                    mode = "transit"
                except:

                    return "error","error","error"
        try:
            fromindex = textlist.index("from")
        except:
            return "error","error","error"
        try:
            toindex = textlist.index("to")
        except:
            return "error","error","error"
        currentlocation = []
        for x in range(fromindex+1,finalindex):
            currentlocation.append(textlist[x])
        destination = []
        for x in range(toindex+1,fromindex):
            destination.append(textlist[x])
        destinationstring = ' '.join(destination)
        currentlocationstring = ' '.join(currentlocation)
        return currentlocationstring,destinationstring,mode
#FinalIndex
    try:
        finalindex = textlist.index("driving")
        
        mode = "driving"
    except:
        try:
            finalindex = textlist.index("walking")
            mode = "walking"
        except:
            try:
                finalindex = textlist.index("transit")
                mode = "transit"
            except:
                return "error","error","error"
    fromindex = 0
    try:
        fromindex = textlist.index("from")
    except:
        print("Error Invalid request")
        return "error","error","error"
    toindex = 0
#To index
    try:
        toindex = textlist.index("to") 
    except:
        return "error","error","error"
    currentlocation = []
    for x in range(fromindex+1,toindex):
        currentlocation.append(textlist[x])
    destination = []
    for x in range(toindex+1,finalindex):
        destination.append(textlist[x])
    destinationstring = ' '.join(destination)
    currentlocationstring = ' '.join(currentlocation)
    print(currentlocationstring,destinationstring,mode)
    return currentlocationstring,destinationstring,mode

def replaceString(text,index=0,replacement=''):
    return '%s%s%s'%(text[:index],replacement,text[index+1:])
def stripBasic(final,brackets=True,colons = True):
    final = final.replace("}","")
    final = final.replace("{'title'","")
    final = final.replace(",'plaintext':","")
    final = final.replace("'","")
    final = final.replace("title","")
    final = final.replace("plaintext","")
    final = final.replace("{","")    
    if colons == True:
        final = final.replace(":","")
    final = final.replace(" ),","")
    final = final.replace("\\n","\n ")
    final = final.replace(" , ","")
    final = final.replace("primary True, ","")
    return final
def personFormat(final,parsedjson):
    #Get notable fact and THEN strip.
    if (has(parsedjson,"Notable facts")):
        final = final+"\n\nInfo\n"+find(parsedjson,"Notable facts")
    if(has(parsedjson,"Awards")):
        final = final+"\n\nAwards\n"+find(parsedjson,"Awards")

    
    final = final.replace(" age ","\nAge: ")
    final = final.replace(" full name |","Full Name:")
    final = final.replace(" date of birth |","Date Of Birth: ")
    final = final.replace(" place of birth |","Place of Birth: ")
    final = final.replace("place of death |","Place of Death: ")
    final = final.replace("date of death |","Date of Death: ")
    final = final.replace("category | year | film","Organized By:\nCategory | Year | Film\n")
    final = final.replace("music","Music")
    final = final.replace("movie","Movie")
    final = final.replace("(year indicates year of award ceremony","")
    return final
def leaderFormat(final,parsedjson):
    #Leadership Positions
    if(has(parsedjson,"Leadership")):
        final = final+"\n\n"+find(parsedjson,"Leadership")

   
    final = final.replace("official position | country | political affiliation | start date | end date","Organized by:\nPosition | Country | Affiliation | Start Date | End Date\n")
    final = final.replace("political affiliation |", "Affiliation: ")
    final = final.replace("official position | country | start date | end date","Organized by:\nOfficial Position | Country | Start Date | End Date\n")
    final = final.replace("start date |","Start Date:")
    final = final.replace("official position |", "Official Position: ")
    final = final.replace("country |","Country: ")
    final = final.replace("end date |","End Date: ")
    final = final.replace("United States | United States","United States")
    final = final.replace("Affiliation:  |","Affiliation: ")
    final = final.replace("Conservative | Conservative","Conservative")
    final = final.replace("Prime Minister | Prime Minister","Prime Minister")
    final = final.replace("United Kingdom | United Kingdom","United Kingdom")
    return final


def weatherFormat(final):
    final = final.replace(" temperature |","Temperature: ")
    final = final.replace("relative humidity |","Relative Humidity: ")
    final = final.replace("dew point","\nDew Point: ")
    final = final.replace("conditions |","Conditions: ")
    final = final.replace("wind chill","Wind Chill: ")
    final = final.replace("wind speed |","Wind Speed: ")
    final = final.replace("%","%\n")
    final = final.replace(" (\n","")
    final = final.replace(")","")
    final = final.replace("(","")
    return final

def musicFormat(final,parsedjson):
    if(has(parsedjson,"Music albums")):
        final = final+"\n\nAlbums\n"+find(parsedjson,"Music albums")
    return final
def placeFormat(final,parsedjson):
    if(has(parsedjson,"Administrative regions")):
        final = final+"\n"+find(parsedjson,"Administrative regions")
    if(has(parsedjson,"Current local time")):
        final = final+"\n\nTime\n"+find(parsedjson,"Current local time")
    if(has(parsedjson,"Current weather")):
        final = final+"\n\nWeather\n"+find(parsedjson,"Current weather")
    if(has(parsedjson,"Enroll")):
        final = final+"\n\nEnrollment\n"+find(parsedjson,"Enroll")
    if(has(parsedjson,"Tuition")):
        final = final+"\n\nTuition\n"+find(parsedjson,"Tuition")
    if(has(parsedjson,"Accrediting")):
        final = final+"\n\nAccrediting\n"+find(parsedjson,"Accrediting")

    final = final.replace("graduation rate |","Graduation Rate: ")
    final = final.replace("local undergraduate students |","Local Undergrads: ")
    final = final.replace("local graduate students |","Local Grads: ")
    final = final.replace("international undergraduate students |","International Undergrads: ")
    final = final.replace("international graduate students |","International Grads: ")
    final = final.replace("undergraduate students |","Undergrad Students: ")
    final = final.replace("all students |","All Students: ")
    final = final.replace("full-time students |","Full Time Students: ")
    final = final.replace("part-time students |","Part Time Students: ")
    final = final.replace("graduate students |","Graduate Students: ")
    final = final.replace("location |","Location: ")
    final = final.replace("website |","Website: ")
    final = final.replace("type |","Type: ")
    final = final.replace("year founded |","Year Founded: ")
    final = final.replace("gender of student body |","Gender of Student Body: ")
    final = final.replace(" temperature |","Temperature: ")
    final = final.replace("relative humidity ","Relative Humidity: ")
    final = final.replace("dew point","\nDew Point: ")
    final = final.replace("conditions |","Conditions: ")
    final = final.replace("wind chill","Wind Chill: ")
    final = final.replace("wind speed |","Wind Speed: ")
#    final = final.replace("%","%\n")
    final = final.replace(" , ","")
    final = final.replace(" ,","")
    final = final.replace("region |","Region: ")
    final = final.replace("country |","Country: ")
    final = final.replace("city population |","Population: ")
    final = final.replace("country rank","\nCountry Rank: ")
    final = final.replace("metro area population |","Metro Population: ")
    final = final.replace("people (","people\n(")
    #final = final.replace(": ","")
    final = final.replace(" :","")
    return final
def jobFormat(final,parsedjson):
    final = ""
    try:
        final = parsedjson['queryresult']['pods'][0]['definitions']['word'] +"\n"+parsedjson['queryresult']['pods'][0]['definitions']['desc']
        
    except:
        try:
            decisor = 1000
            for x in range(15):
                if "Sub-specialties" in str(parsedjson['queryresult']['pods'][x]['title']):
                    decisor = x
                    break
            final = str(parsedjson['queryresult']['pods'][decisor]['definitions'][0]['desc'])
        except:
             
            print("No description found..")
    if(has(parsedjson,"Employment summary")):
        final = final+"\n\nEmployment\n"+find(parsedjson,"Employment summary")
    #replace and make it look nicer
    final = final.replace("people employed |","People Employed: ")
    final = final.replace("yearly change |","Yearly Change: ")
    final = final.replace("workforce fraction |","Workforce Fraction: ")
    final = final.replace("median wage yearly change |","MW Yearly Change: ")
    final = final.replace("median wage |","Median Wage: ")
    final = final.replace("range |","Range: ")
    final = final.replace(" |",": ")
    return final

def chemicalFormat(final,parsedjson):
    final = str(parsedjson['queryresult']['pods'][0]['subpods'][0])
    final = stripBasic(final)
    if(has(parsedjson,"Chemical names")):
        final = final+"\n\nFormulation\n"+find(parsedjson,"Chemical names")
    if(has(parsedjson,"Basic properties")):
        final = final+"\n\nProperties\n"+find(parsedjson,"Basic properties")
    if(has(parsedjson,"Drug interactions")):
        final = final+"\n\nDrug Interactions\n"+find(parsedjson,"Drug interactions")
    if(has(parsedjson,"Basic drug")):
        final = final +"\n\nDrug Info\n"+find(parsedjson,"Basic drug")
    if(has(parsedjson,"Safety")):
        final = final+"\n\nSafety\n"+find(parsedjson,"Safety")
    if(has(parsedjson,"Toxicity")):
        final = final +"\n\nToxicity\n"+find(parsedjson,"Toxicity")
    if(has(parsedjson,"Ion equivalents")):
        final = final+"\n\nIon Equals\n"+find(parsedjson,"Ion equivalents")


    final = final.replace("approval status |","Approval Status: ")
    final = final.replace("drug categories |","Categories: ")
    final = final.replace("dosage forms |","Dosage Forms: ")
    final = final.replace("lethal dose |","Lethal Dose: ")
    final = final.replace("solubility in water |","Solubility: ")
    final = final.replace("_","")
    final = final.replace("formula |","Formula: ")
    final = final.replace("name |","Name: ")
    final = final.replace("molar mass |","Molar Mass: ")
    final = final.replace("phase |","Phase: ")
    final = final.replace("melting point |","Melting Point: ")
    final = final.replace("boiling point |","Boiling Point: ")
    final = final.replace("density |","Density: ")
    final = final.replace("flash point |","Flash Point: ")
    final = final.replace("classes |","Classes: ")
 
    return final




def movieFormat(final,parsedjson):
    if(has(parsedjson,"Box office")):
        final = final +"\n\nPerformance\n"+find(parsedjson,"Box office performance")
    if(has(parsedjson,"Cast")):
        final = final+"\n\nCast\n"+find(parsedjson,"Cast")
    if(has(parsedjson,"Awards")):
        final = final+"\n\nAwards\n"+find(parsedjson,"Awards")
    final = stripBasic(final,False)
    final = final.replace("title |","Title: ")
    final = final.replace("director |","Director: ")
    final = final.replace("release date |","Release Date: ")
    final = final.replace("runtime |","Runtime: ")
    final = final.replace("writers |","Writers: ")
    final = final.replace("genres |","Genres: ")
    final = final.replace("MPAA rating |","Rating: ")
    final = final.replace("production budget |","Budget: ")

    final = final.replace("total receipts |","Total Receipts: ")
    final = final.replace("highest receipts |","Highest Receipts: ")
    final = final.replace("higest rank |","Highest Rank: ")
    final = final.replace("maximum number of screens |","Maximum Screens: ")
    final = final.replace("highest average receipts per screen |","Highest RPS: ")
    
    final = final.replace("network |","Network: ")
    final = final.replace("air dates |","Air Dates: ")
    final = final.replace("episode running time |","Episode Time: ")
    final = final.replace("seasons |","Seasons: ")
    final = final.replace("episodes |","Episodes: ")
    final = final.replace("actor | character(s)","Organized By:\n Actor | Character\n")
    final = final.replace("category | recipient","Organized By:\n Category | Recipient\n")
    final = final.replace("directing","Directing")
    final = final.replace("actress","Actress")
    final = final.replace("actor","Actor")
    final = final.replace("film editing","Film Editing")
    final = final.replace("makeup","Makeup")
    final = final.replace("best","Best")
    final = final.replace("writing","Writing")
    final = final.replace("music","Music")
    return final


def getDirections(inputtext,recipient):
    current,destination,mode = getLocations(inputtext)
    if (current or destination or mode) == "error":
        return "Your directions request is not formatted properly! \nFormat it like this\n -> Directions from <YOUR CURRENT DESTINATION> to <WHERE YOU WANT TO GO> <'walking','driving', or 'transit'>\n\nFor Example\n'Directions from the CN Tower to the Woodlands Secondary School transit'"
    current = current.replace(" ","+")
    destination = destination.replace(" ","+")
    url = "https://maps.googleapis.com/maps/api/directions/json?origin="+current+"&destination="+destination+"&mode="+mode+"&key=REDAC"
    try:
        req = urllib.request.Request(url)
        r = urllib.request.urlopen(req).read()
        parsedjson = json.loads(r.decode('utf-8'))
        
        directionlist = []
        try:
            for x in range(1000):
                if (mode == "transit"):
                    try:
                        
                        instructions = parsedjson['routes'][0]['legs'][0]['steps'][x]['html_instructions']
                      
                        busname = parsedjson['routes'][0]['legs'][0]['steps'][x]['transit_details']['headsign']
                        
                        time = parsedjson['routes'][0]['legs'][0]['steps'][x]['transit_details']['departure_time']['text']
                        
                        stop = parsedjson['routes'][0]['legs'][0]['steps'][x]['transit_details']['departure_stop']['name']
                        
                        arrival = parsedjson['routes'][0]['legs'][0]['steps'][x]['transit_details']['arrival_stop']['name']
                        
                        final = "Take Bus "+busname+" from "+stop+" which arrives at "+time +". Get off at "+arrival+"\n"
                        
                        directionlist.append(final)
                    except:
                        directionlist.append(parsedjson['routes'][0]['legs'][0]['steps'][x]['html_instructions'])
                else:
                    directionlist.append(parsedjson['routes'][0]['legs'][0]['steps'][x]['html_instructions'])

        except:
            print("Reached end")
        finalstring = ""
        for direction in directionlist:
           
            index = directionlist.index(direction)
          
            try:
                directionlist[index] = re.sub('<[^<]+?>', '', direction)
            except:
                string1 = "This is just a placeholder string, fml"
            
            finalstring = finalstring+directionlist[index]+"\n"
        finalstring = finalstring.replace("Restricted usage road","\n(Restricted Usage Road)")
        finalstring = finalstring.replace("Toll road"," (Toll)")
        finalstring = finalstring.replace("Take","\nTake")
        finalString = finalstring.replace("EContinue","E \nContinue")
        finalstring = finalstring.replace("WContinue","W \nContinue")
        finalstring = finalstring.replace("NContinue","M\n Continue")
        finalstring = finalstring.replace("SContinue","S\n Continue")
        finalstring = finalstring.replace("Destination","\nDestination")
        savedname = 0
        try:
            if ("picture" or "image") in inputtext:
                newurl = "https://maps.googleapis.com/maps/api/staticmap?&size=400x400&markers=color:blue%7Clabel:A%7C"+current+"&markers=color:red%7Clabel:B%7C"+destination+"&path=color:0x0000ff%7Cweight:5%7C"+current+"%7C"+current+"%7C"+destination+"%7C"+destination+"&key=REDAC"
                buffer = BytesIO(urllib.request.urlopen(newurl).read())
                image = Image.open(buffer)
                rand = random.randint(0,10000)
                savedname = rand
                image.save("/var/www/html/"+str(rand)+".png")
                sendPicture(recipient,savedname)
        except:
             print("Couldn't obtain a picture")
        sendMessage(recipient,"I have found directions for your travel.\nPlease wait while I find the most efficient route")
        print("OUTPUT: "+finalstring)
        return finalstring
    except:
        return "Your directions request is not formatted properly! \nFormat it like this\n -> Directions from <YOUR CURRENT DESTINATION> to <WHERE YOU WANT TO GO> <'walking','driving', or 'transit'>\n\nFor Example\n'Directions from the CN Tower to the Woodlands Secondary School transit'"
#Why did we do dinosaurs? idk
def dinosaurFormat(final,parsedjson):
    if(has(parsedjson,"Taxonomy")):
        final = final+"\n\nTaxonomy\n"+find(parsedjson,"Taxonomy")
    if(has(parsedjson,"Properties")):
        final = final+"\n\nProperties\n"+find(parsedjson,"Properties")
    if(has(parsedjson,"Other members of family")):
        final = final+"\n\nFamily Members\n"+find(parsedjson,"Other members of family")
    if(has(parsedjson,"Other members of genus")):
        final = final+"\n\nGenus Members\n"+find(parsedjson,"Other members of genus")
    final = final.replace("discovery country |","Discovery Country: ")
    final = final.replace("order |","Order: ")
    final = final.replace("kingdom |","Kingdom: ")
    final = final.replace("class |","Class: ")
    final = final.replace("genus |","Genus: ")
    final = final.replace("family |","Family: ")
    final = final.replace("phylum |","Phylum: ")
    final = final.replace("species |","Species: ")
    final = final.replace("countries found in |","Countries: ")
    final = final.replace("period |","Period: ")
    final = final.replace("diet |","Diet: ")
    final = final.replace("weight |","Weight: ")
    final = final.replace("full length |","Full Length: ")
    return final
def diseaseFormat(final,parsedjson):
    final = ""
    if(has(parsedjson,"Definition")):
        final = final+"\n\nDefinition\n"+find(parsedjson,"Definition")
    else:
        final = final+"Definition\n"+str(parsedjson['queryresult']['pods'][0]['subpods'][0])
        final = stripBasic(final)
    if(has(parsedjson,"Medical codes")):
        final = final+"\n\nCodes\n"+find(parsedjson,"Medical codes")
    if(has(parsedjson,"Drugs prescribed")):
        final = final+"\n\nPrescribed Drugs"+find(parsedjson,"Drugs prescribed")
    if (has(parsedjson,"Associated genes")):
        final = final+"\n\nAssociated Genes\n"+find(parsedjson,"Associated genes")
    final = final.replace(" | male | female | all","Organized By:\nMale% | Female% | All%\n\n")
    
    return final
def speciesFormat(final,parsedjson):
    if(has(parsedjson,"Taxonomy")):
        final = final+"\n\nTaxonomy\n"+find(parsedjson,"Taxonomy")
    if(has(parsedjson,"Biological properties")):
        try:
            decisor = 100
            for x in range(20):
                if ("Biological properties" in str(parsedjson['queryresult']['pods'][x]['title'])):
                    decisor = x
                    break
            basicprops = str(parsedjson['queryresult']['pods'][decisor]['subpods'][0])
            final = final+"\n\n"+basicprops
            final = stripBasic(final)
            physicalprops = str(parsedjson['queryresult']['pods'][decisor]['subpods'][1])
            final = final+"\n\n"+physicalprops
            final = stripBasic(final)
        except:
            string2 = "This is literally another placeholder string to skip over this, fml, does continue work here???"
    if(has(parsedjson,"Other members of genus")):
        final = final+"\n\nGenus Members\n"+find(parsedjson,"Other members of genus")
    
    if(has(parsedjson,"Other members of species")):
        final = final+"\n\nSpecies Members\n"+find(parsedjson,"Other members of species")
    final = final.replace("discovery country |","Discovery Country: ")
    final = final.replace("order |","Order: ")
    final = final.replace("kingdom |","Kingdom: ")
    final = final.replace("class |","Class: ")
    final = final.replace("genus |","Genus: ")
    final = final.replace("family |","Family: ")
    final = final.replace("phylum |","Phylum: ")
    final = final.replace("species |","Species: ")
    final = final.replace("countries found in |","Countries: ")
    final = final.replace("period |","Period: ")
    final = final.replace("diet |","Diet: ")
    final = final.replace("maximum recorded weight |","Max Weight: ")
    final = final.replace("weight (female) |","Weight (Male): ")
    final = final.replace("weight (male) |","Weight (Female): ")
    final = final.replace("weight |","Weight: ")
    final = final.replace("full length |","Full Length: ")
    final = final.replace("Basic properties,","Basic Properties\n")
    final = final.replace("Physical properties,","Physical Properties\n")
    final = final.replace("maximum recorded lifespan |","Max Lifespan: ")
    final = final.replace("lifespan |","Lifespan: ")
    final = final.replace("maximum recorded length |","Max Length: ")
    final = final.replace("length |","Length: ")
    final = final.replace("height |","Height: ")
    return final
def celestialFormat(final,parsedjson):
    final = ""
    final = str(parsedjson['queryresult']['pods'][0]['subpods'][0])
    final = stripBasic(final)
    if (has(parsedjson,"Orbital properties")):
        final = final+"\n\nOrbital Properties\n"+find(parsedjson,"Orbital properties")
    if(has(parsedjson,"Properties")):
        final = final+"\n\nProperties\n"+find(parsedjson,"Properties")
    if (has(parsedjson,"Physical properties")):
        final = final+"\n\nPhysical Properties\n"+find(parsedjson,"Physical properties")
    if(has(parsedjson,"Atmosphere")):
        final = final+"\n\nAtmosphere\n"+find(parsedjson,"Atmosphere")
    if(has(parsedjson,"Probes")):
        final = final+"\n\nProbes\n"+find(parsedjson,"Probes")
    if(has(parsedjson,"Probe properties")):
        final = final+"\n\nProperties\n"+find(parsedjson,"Probe properties")
    if (has(parsedjson,"Mission properties")):
        final = final+"\n\nMission Properties\n"+find(parsedjson,"Mission properties")
    if (has(parsedjson,"Star properties")):
        final = final+"\n\nStar Properties\n"+find(parsedjson,"Star properties")
    final = final.replace("current distance from Earth |","Distance from Earth: ")
    final = final.replace("average distance from Earth |","Avg. Distance from Earth: ")
    final = final.replace("current distance from Sun |","Distance from Sun: ")
    final = final.replace("largest distance from orbit center |","Largest Orbit Center Distance: ")
    final = final.replace("nearest distance from orbit center |","Nearest Orbit Center Distance: ")
    final = final.replace("orbital period |","Orbital Period: ")
    final = final.replace("equatorial radius |","Equatorial Radius: ")
    final = final.replace("mass |","Mass: ")
    final = final.replace("rotation period |","Rotation Period: ")
    final = final.replace("number of moons |","Number of Moons: ")
    final = final.replace("age |","Age: ")
    final = final.replace("atmospheric pressure |","Atmospheric Perssure: ")
    final = final.replace("minimum temperature |","Min Temperature: ")
    final = final.replace("maximum temperature |","Max Temperature: ")
    final = final.replace("average temperature |","Avg Temperature: ")
    final = final.replace("average radius |","Avg Radius: ")
    final = final.replace("alternate names |","Alt. Names: ")
    final = final.replace("absolute magnitude |","Absolute Magnitude: ")
    final = final.replace("type |","Type: ")
    final = final.replace("apparent magnitude |","Apparent Magnitude: ")
    final = final.replace("radial velocity |","Radial Velocity: ")
    final = final.replace("redshift |","Redshift: ")
    final = final.replace("targets |","Targets: ")
    final = final.replace("mass |","Mass: ")
    final = final.replace("length |","Length: ")
    final = final.replace("width |","Width: ")
    final = final.replace("height |","Height: ")
    final = final.replace("heliocentric velocity |","Heliocentric Velocity: ")
    final = final.replace("orbital inclination |","Orbital Inclination: ")
    final = final.replace("power source |","Power Source: ")
    final = final.replace("launch date |","Launch Date: ")
    final = final.replace("spectral class |","Spectral Class: ")
    final = final.replace("effective temperature |","Effective Temperature: ")
    final = final.replace("main sequence lifetime |","Main Sequence Lifetime: ")
    final = final.replace("end state |","End State: ")
    final = final.replace("name |","Name: ")
    return final
def anatomyFormat(final,parsedjson):
    if(has(parsedjson,"Functional description")):
        final = final+"\n\nDescription\n"+find(parsedjson,"Functional description")
    if (has(parsedjson,"Typical physical characteristics")):
        final = final+"\n\nPhysical\n"+find(parsedjson,"Typical physical characteristics")
    if (has(parsedjson,"Constitutional parts")):
        final = final+"\n\nParts\n"+find(parsedjson,"Constitutional parts")
    if (has(parsedjson,"Connections")):
        final = final +"\n\nConnections\n"+find(parsedjson,"Connections")

    final = final.replace("surface area |", "Surface Area: ")
    final = final.replace("volume |","Volume: ")
    final = final.replace("area |","Area: ")
    final = final.replace("shape |","Shape: ")
    final = final.replace("mass |","Mass: ")
    final = final.replace("length |","Length: ")
    final = final.replace("width |","Width: ")
    final = final.replace("depth |","Depth: ")
    final = final.replace("density |","Density: ")
    final = final.replace("weight percentage of total body |","Body weight percentage: ")
    return final
#Clean up the message that was recieved from JSON all messy
def clean(final, datatype,parsedjson,recipient):
#Clean the core stuff
    final = stripBasic(final)
    #For people
    #For temperature
    if "Weather" in datatype:
        final = weatherFormat(final)
    elif "Star" in datatype:
        sendMessage(recipient,"Please wait while I gather information about that celestial body")
        final = celestialFormat(final,parsedjson)
    elif "StarCluster" in datatype:
        sendMessage(recipient,"Please wait while I gather information about that celestial body")
        final = celestialFormat(final,parsedjson)
    elif "DeepSpaceProbe" in datatype:
        sendMessage(recipient,"Please wait while I gather information about that probe")
        final = celestialFormat(final,parsedjson)
    elif "Planet" in datatype:
        sendMessage(recipient,"Please wait while I gather information about that planet")
        final = celestialFormat(final,parsedjson)
    elif "TelevisionProgram" in datatype:
        sendMessage(recipient,"Please wait while I gather information about that movie/show")
        final = movieFormat(final,parsedjson)
    elif "Leader" in datatype:
        sendMessage(recipient,"Please wait while I gather the information about that political figure")
        final = leaderFormat(final,parsedjson)
        final = personFormat(final,parsedjson)
    elif "MusicAct" in datatype:
        sendMessage(recipient,"Please wait while I gather the information about that artist")
        final = musicFormat(final,parsedjson)
        final = personFormat(final,parsedjson)
    elif ("People" in datatype) and ("Basic movie" not in str(parsedjson['queryresult']['pods'][1]['title'])):
        sendMessage(recipient,"Please wait while I gather information about that person")
        final = personFormat(final,parsedjson)
    elif (("Movie" and "Person") in datatype) and ("Basic movie" not in str(parsedjson['queryresult']['pods'][1]['title'])):
        sendMessage(recipient,"Please wait while I gather information about that actor")
        final = personFormat(final,parsedjson)
    elif ("Movie") in datatype:
        sendMessage(recipient,"Please wait while I gather information about that movie/show")
        final = movieFormat(final,parsedjson)
    elif ("City" or "Country") in datatype:
        sendMessage(recipient,"Please wait while I gather information about that place")
        final = placeFormat(final,parsedjson)
    elif "Anatomy" in datatype:
        sendMessage(recipient,"Please wait while I gather more information about that anatomical structure")
        final = anatomyFormat(final,parsedjson)
    elif "ExpandedSalary" in datatype:
        sendMessage(recipient,"Please wait while I gather information on that occupation")
        final = jobFormat(final,parsedjson)
    elif ("Chemical" or "MatterPhase") in datatype:
        sendMessage(recipient,"Please wait while I gather information on that substance")
        final = chemicalFormat(final,parsedjson)
    elif "Dinosaur" in datatype:
        sendMessage(recipient,"Please wait while I gather information on that dinosaur")
        final = dinosaurFormat(final,parsedjson)
    elif "Disease" in datatype:
        sendMessage(recipient,"Please wait while I gather information on that disease")
        final = diseaseFormat(final,parsedjson)
    elif "Species" in datatype:
        sendMessage(recipient,"Please wait while I gather information on that species")
        final = speciesFormat(final,parsedjson)
    final = final.rstrip(',')
    print("OUTPUT: "+final)
    return final


#A Fallback function???
def sendCall(recipient,filename):
    client = Client(account_sidinuse, auth_tokeninuse)

    call = client.calls.create(
        to=recipient,
        from_=phoneinuse,
        url="http://ovh.kaveenk.me/"+filename+".xml")
def sendPicture(recipient,filename):

    client = Client(account_sidinuse,auth_tokeninuse)
    message = client.api.account.messages.create(
        to=recipient,
        from_=phoneinuse,
        media_url="http://ovh.kaveenk.me/"+str(filename)+".png")
    print("Dispatched a map image to "+str(recipient)+" "+message.sid)
def sendMessage(recipient,body):

    client = Client(account_sidinuse, auth_tokeninuse)
    message = client.messages.create(
        recipient,
        body=body,
        from_=phoneinuse)
    print("Dispatched a message to "+str(recipient)+" "+message.sid)
#inspired by starterhacks
def imageSend(recipient,body):
    url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyA8c44pFXOBhe0SccUmvm_iySAfITJ8X2k&cx=0012622134167189936083:kvvtebwdwcq&q="+urllib.parse.quote(body)
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    picturepath = None
    for x in range(0,10):
        try:
            picturepath = data['items'][x]['pagemap']['cse_image'][0]['src']
            break
        except:
            print("Couldn't find the image")
            sendMessage(recipient,"I couldn't find an image of this nature")
            return
    client = Client(account_sidinuse,auth_tokeninuse)
    message = client.api.account.messages.create(
        to=recipient,
        from_=phone,
        media_url=picturepath)
    print("Dispatched an image to "+str(recipient)+ " "+message.sid)

#Full results from wolfram full results API
def fullResults(inputtext,appid,recipient):
    global retried,appid1,appid2

    #Replace things with apostrophes
    inputtext = inputtext.strip()
    inputtext = inputtext.replace("Whats","What is")
    inputtext = inputtext.replace("Whos","Who is")
    inputtext = inputtext.replace(" ","+")

   
    url = "https://api.wolframalpha.com/v2/query?input="+inputtext+"&format=plaintext&output=JSON&appid="+appid

    try:
        
        req = urllib.request.Request(url)
      
        r = urllib.request.urlopen(req).read()

        parsedjson = json.loads(r.decode('utf-8'))
        
        returner = parsedjson['queryresult']['pods'][1]['subpods'][0]
        datatype = str(parsedjson['queryresult']['datatypes'])
       
        final = str(returner)
        
        
        final = clean(final,datatype,parsedjson,recipient)

  #      final = final.replace("\n2","")
 #       final = final.replace("\n3","")
#        final = final.replace("\n","")
        return final
    except:
        return "I'm not sure how to answer that... \nText 'COMMANDS' to see the things I can do\nMake sure to have no apostrophes (') in your message!"

#Short results.. for use later..?
def shortResults(inputtext):
    inputtext = inputtext.strip()
    inputtext = inputtext.replace(" ","+")
    url = "https://api.wolframalpha.com/v1/result?i="+inputtext+"%3F&appid=TTTYYK-LKR85VWW3Y"
    try:
        uf = urllib.request.urlopen(url)
    except:
        print("Simple result unattainable, trying full results API")
    #Full results api code here..
        return fullResults(inputtext,appid2)
    html = uf.read()
    html = str(html)
    html = html.replace("b","")
    html = html.replace("'","")
    if (html == "1 word definition"):
        html = fullResults(inputtext,appid2)
    print("OUTPUT: "+html)
    return html

def recentNews(recipient):
    top_headlines = newsapi.get_top_headlines(country='ca')
    client = Client(account_sid, auth_token)
    try:
        for x in range(0,3):
            client.messages.create(
                to=recipient,
                from_=phone,
                body=top_headlines['articles'][x]['title'] +"\n\n"+top_headlines['articles'][x]['description']+"\n"+top_headlines['articles'][x]['url']
            )
            print("OUTPUT: "+top_headlines['articles'][x]['title'])
    except:
        string1 = "another fucking placeholder string"
def newsAbout(query,recipient):


    url = "https://newsapi.org/v2/everything?q="+urllib.parse.quote(query)+"&sortBy=relevance&apiKey=63fa2b27a22749928170f628bba66301"
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req).read()
    top_headlines = json.loads(response.decode('utf-8'))


    #Headline 1
    client = Client(account_sid, auth_token)
    try:
        for x in range(0,2):
            client.messages.create(
                to=recipient,
                from_=phone,
                body=top_headlines['articles'][x]['title'] +"\n\n"+top_headlines['articles'][x]['description']+"\n"+top_headlines['articles'][x]['url']
            )
            print("OUTPUT: "+top_headlines['articles'][x]['title'])

    except:
        string1 = "ANOTHER PLACEHOLDER STRING??"



app = Flask(__name__)

@app.route("/twilio", methods=['GET', 'POST'])
def sms_reply():
    global appid2,appid1
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    body = request.form['Body']
    recipient = request.form['From']
    resp = MessagingResponse()

    liststring = body.split(" ")
    print("INPUT: "+body)
    #Get rid of the apostrophes in the identifiers..
    if ((len(liststring[0]) == 6) and ("here" not in liststring[0]) and "hat" in liststring[0]):
        liststring[0] = replaceString(liststring[0],4)
    elif ((len(liststring[0]) == 5) and ("here" not in liststring[0]) and "ho" in liststring[0]):
        liststring[0] = replaceString(liststring[0],3)
    elif ( (len(liststring[0]) == 7) and ("here" in liststring[0])):
        liststring[0] = replaceString(liststring[0],5)
    body = ' '.join(liststring)
    if "directions" in body.lower():
        solved = getDirections(body,recipient)
        resp.message(solved)
        return str(resp)
    body = body.strip(" ")
    if (body.lower().startswith("show me a picture of") or body.lower().startswith("picture of") or body.lower().startswith("show me") or body.lower().startswith("show me an image of") or body.lower().startswith("pic of") or body.lower().startswith("image of") or body.lower().startswith("show me a picture of") or body.lower().startswith("show me an image of") or body.lower().startswith("show me pictures of") or body.lower().startswith("show me images of") or body.lower().startswith("send me a picture") or body.lower().startswith("send me an image")):
        body = body.lower()
        body = body.replace("send me a picture of an","")
        body = body.replace("send me an image of an","")
        body = body.replace("send me a picture of a","")
        body = body.replace("send me an image of a","")
        body = body.replace("send me a picture of","")
        body = body.replace("send me an image of","")

        body = body.replace("show me a picture of an","")
        body = body.replace("show me an image of an","")
        body = body.replace("show me a picture of a","")
        body = body.replace("show me an image of a","")

        body = body.replace("show me pictures of","")
        body = body.replace("show me images of","")
        body = body.replace("show me a picture of","")
        body = body.replace("picture of","")
        body = body.replace("show me","")
        body = body.replace("image of","")
        body = body.replace("pic of","")
        body = body.replace("show me an image of","")

        sendMessage(recipient,"Fetching image, this might take a bit")
        if " " in body:
            body = body.replace(" ","")
        imageSend(recipient,body)
        return str(resp)
    if (body.lower().startswith("news about")):
        body = body.lower()
        #Format!!
        final = body.replace("news about","")
        sendMessage(recipient,"Fetching News")
        newsAbout(final,recipient)
        return str(resp)
    if (body.lower().startswith("recent news")):
        sendMessage(recipient,"Fetching News")
        recentNews(recipient)
        body = body.lower()
        return str(resp)
    if (len(body) == 4 and body.lower() == "news"):
        sendMessage(recipient,"Fetching News")
        recentNews(recipient)
        return str(resp)
    helpidentifiers = ["HELP","help","how do i use this","what is this","commands","INFO","Commands","COMMANDS"]
    if (body.lower() == "example" or body.lower() == "examples"):
        sendMessage(recipient,"Directions:\n directions from <current> to <destination> <driving/transit/walking>\n\nInformation:\nWho is Donald Trump?\nWhat is the speed of light?\nHow old is Obama?\nWaterloo University information\nWeather in Toronto\nInformation about Toronto\n\nImages:\nShow me a picture of <query>\n\nNews:\nRecent News\nNews about <subject>")
        return str(resp)
    for identifier in helpidentifiers:
        if identifier in body:
            sendMessage(recipient,"Welcome to CloudSMS, you can do many things, such as view the weather, get recent news, get directions, find images, and find information about people, places, things, and more! Type EXAMPLES for some examples")
            return str(resp)
    identifiers = ["who r u","who are u","who are you","who art thou","qui est tu","whp are you","who you"]
    for identifier in identifiers:
        if identifier in body.lower():
            resp.message("This is CloudSMS by team JAKS for StarterHacks 2018")
            return str(resp)

    if ("how do i get to" or "how do i go to") in body.lower():
        resp.message("That is not how you ask for directions!\n Ask like this:\n Directions from <current location> to <destination>")
        return str(resp)
    #Parse to the fullResults API and get the results to set in the XML.


    #IMPORTANT LINE
    solved = fullResults(body,appid2,recipient)



    #If wolfram fucks up or something
    if "data not available nodata" in solved:
        resp.message("This data isn't available at the moment, sorry :(")
    else:
        resp.message(solved)

    return str(resp).rstrip(",")

if __name__ == "__main__":
    global retried,appid1,appid2
    appid1 = "TTTYYK-LKR85VWW3Y"
    appid2 = "TTTYYK-LKR85VWW3Y"

    retried = False
    app.run(debug=True,host='0.0.0.0',port=44)



