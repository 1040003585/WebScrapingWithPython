# -*- coding: utf-8 -*-

import csv
from datetime import datetime, timedelta
import string
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except locale.Error:
    pass
from gluon.dal import Field
from gluon.html import *
from gluon.http import HTTP



def get_id(args):
    """Return ID at first arg if defined and a number, else zero
    """
    id = 0
    if args:
        try:
            id = to_int(args[0])
        except ValueError:
            pass
    return id


def to_int(s):
    """Return integer from this string
    """
    return int('0' + ''.join(c for c in s if c.isdigit()))


def safe(*words):
    """Return string safe for using in URL
    """
    safe_chars = string.letters + string.digits + '-'
    result = []
    for word in words:
        result.append(''.join(c for c in str(word).strip().replace(' ', '-') if c in safe_chars))
    return '-'.join(result)


def format_records(records, num_columns=2):
    trs = []
    for i, record in enumerate(records):
        if i % 2 == 0:
            tds = []
        tds.append(XML(record.pretty_link))
        if i % 2 == num_columns - 1:
            trs.append(TR(tds))
    return TABLE(trs)


class Places:
    def __init__(self, db, expire_db_secs=3600):
        """
        expire_db_secs: how long before refresh database
        """
        self.db = db
        self.fields = 'iso', 'country', 'capital', 'area', 'population', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours'
        self.numeric_fields = 'area', 'population'
        db.define_table('places', 
            Field('created_on', 'datetime', writable=False, readable=False, default=datetime.now),
            Field('country_id', 'integer', writable=False, readable=False),
            Field('national_flag', writable=False, represent=lambda path: IMG(_src=path)),
            Field('area', 'double', represent=lambda area: locale.format("%d", area, grouping=True) + ' square kilometres'),
            Field('population', 'integer', represent=lambda pop: locale.format("%d", pop, grouping=True)),
            #Field('population', 'integer', represent=lambda pop: '{0:,d}'.format(pop)),
            *[Field(field, 'string') for field in self.fields if field not in self.numeric_fields]
            #format=lambda record: XML('<a href="%(pretty_url)s">%(country)s (%(iso)s)</a>' % record)
        )
        # define user friendly url for accessing a place
        db.places.pretty_url = Field.Virtual('pretty_url', lambda record: URL(c='default', f='view', extension=False, args=safe(record.places.country, record.places.country_id)))
        db.places.pretty_link = Field.Virtual('pretty_link', lambda record: str(\
            DIV(
                A(
                    IMG(_src=record.places.national_flag), 
                    #db.places.national_flag.represent(record.national_flag),
                    ' %s' % (record.places.country), 
                    _href=URL(c='default', f='view', extension=False, args=safe(record.places.country, record.places.country_id))
                )
            )
        ))
        db.places.continent.represent = lambda continent: A(continent, _href=URL(f='continent', args=continent))
        db.places.neighbours.represent = lambda neighbours: DIV(
            [A(neighbour + ' ', _href=URL(f='iso', args=neighbour)) for neighbour in neighbours.split(',')]
        ) 
        #db.places.pretty_url = Field.Virtual('pretty_url', lambda record: URL(c='default', f='view', extension=False, args=safe(record.places.country, record.places.country_id)))

        if db(db.places).count() == 0:
            self.load()
        else:
            created_on = db(db.places).select().first().created_on
            if created_on is None or created_on + timedelta(seconds=expire_db_secs) < datetime.now():
                self.load()


    def get(self, country_id=None, iso=None):
        if country_id is not None:
            logic = self.db.places.country_id == country_id
        elif iso is not None:
            logic = self.db.places.iso == iso
        place = self.db(logic).select().first()
        if place:
            return place
        else:
            raise HTTP(404, 'Invalid record')
            

    def search(self, logic=None, limitby=None):
        return self.db(logic).select(limitby=limitby, orderby=self.db.places.country_id)


    def load(self):
        """Load places from CSV file and delete any existing
        """
        text = """\
AD,Andorra,Andorra la Vella,468,84000,EU,.ad,EUR,Euro,376,AD###,^(?:AD)*(\d{3})$,ca,"ES,FR"
AE,United Arab Emirates,Abu Dhabi,82880,4975593,AS,.ae,AED,Dirham,971,,,"ar-AE,fa,en,hi,ur","SA,OM"
AF,Afghanistan,Kabul,647500,29121286,AS,.af,AFN,Afghani,93,,,"fa-AF,ps,uz-AF,tk","TM,CN,IR,TJ,PK,UZ"
AG,Antigua and Barbuda,St. John's,443,86754,NA,.ag,XCD,Dollar,+1-268,,,en-AG,
AI,Anguilla,The Valley,102,13254,NA,.ai,XCD,Dollar,+1-264,,,en-AI,
AL,Albania,Tirana,28748,2986952,EU,.al,ALL,Lek,355,,,"sq,el","MK,GR,CS,ME,RS,XK"
AM,Armenia,Yerevan,29800,2968000,AS,.am,AMD,Dram,374,######,^(\d{6})$,hy,"GE,IR,AZ,TR"
AO,Angola,Luanda,1246700,13068161,AF,.ao,AOA,Kwanza,244,,,pt-AO,"CD,NA,ZM,CG"
AQ,Antarctica,,14000000,0,AN,.aq,,,,,,,
AR,Argentina,Buenos Aires,2766890,41343201,SA,.ar,ARS,Peso,54,@####@@@,^([A-Z]\d{4}[A-Z]{3})$,"es-AR,en,it,de,fr,gn","CL,BO,UY,PY,BR"
AS,American Samoa,Pago Pago,199,57881,OC,.as,USD,Dollar,+1-684,,,"en-AS,sm,to",
AT,Austria,Vienna,83858,8205000,EU,.at,EUR,Euro,43,####,^(\d{4})$,"de-AT,hr,hu,sl","CH,DE,HU,SK,CZ,IT,SI,LI"
AU,Australia,Canberra,7686850,21515754,OC,.au,AUD,Dollar,61,####,^(\d{4})$,en-AU,
AW,Aruba,Oranjestad,193,71566,NA,.aw,AWG,Guilder,297,,,"nl-AW,es,en",
AX,Aland Islands,Mariehamn,1580,26711,EU,.ax,EUR,Euro,+358-18,#####,^(?:FI)*(\d{5})$,sv-AX,
AZ,Azerbaijan,Baku,86600,8303512,AS,.az,AZN,Manat,994,AZ ####,^(?:AZ)*(\d{4})$,"az,ru,hy","GE,IR,AM,TR,RU"
BA,Bosnia and Herzegovina,Sarajevo,51129,4590000,EU,.ba,BAM,Marka,387,#####,^(\d{5})$,"bs,hr-BA,sr-BA","CS,HR,ME,RS"
BB,Barbados,Bridgetown,431,285653,NA,.bb,BBD,Dollar,+1-246,BB#####,^(?:BB)*(\d{5})$,en-BB,
BD,Bangladesh,Dhaka,144000,156118464,AS,.bd,BDT,Taka,880,####,^(\d{4})$,"bn-BD,en","MM,IN"
BE,Belgium,Brussels,30510,10403000,EU,.be,EUR,Euro,32,####,^(\d{4})$,"nl-BE,fr-BE,de-BE","DE,NL,LU,FR"
BF,Burkina Faso,Ouagadougou,274200,16241811,AF,.bf,XOF,Franc,226,,,fr-BF,"NE,BJ,GH,CI,TG,ML"
BG,Bulgaria,Sofia,110910,7148785,EU,.bg,BGN,Lev,359,####,^(\d{4})$,"bg,tr-BG","MK,GR,RO,CS,TR,RS"
BH,Bahrain,Manama,665,738004,AS,.bh,BHD,Dinar,973,####|###,^(\d{3}\d?)$,"ar-BH,en,fa,ur",
BI,Burundi,Bujumbura,27830,9863117,AF,.bi,BIF,Franc,257,,,"fr-BI,rn","TZ,CD,RW"
BJ,Benin,Porto-Novo,112620,9056010,AF,.bj,XOF,Franc,229,,,fr-BJ,"NE,TG,BF,NG"
BL,Saint Barthelemy,Gustavia,21,8450,NA,.gp,EUR,Euro,590,### ###,,fr,
BM,Bermuda,Hamilton,53,65365,NA,.bm,BMD,Dollar,+1-441,@@ ##,^([A-Z]{2}\d{2})$,"en-BM,pt",
BN,Brunei,Bandar Seri Begawan,5770,395027,AS,.bn,BND,Dollar,673,@@####,^([A-Z]{2}\d{4})$,"ms-BN,en-BN",MY
BO,Bolivia,Sucre,1098580,9947418,SA,.bo,BOB,Boliviano,591,,,"es-BO,qu,ay","PE,CL,PY,BR,AR"
BQ,"Bonaire, Saint Eustatius and Saba ",,328,18012,NA,.bq,USD,Dollar,599,,,"nl,pap,en",
BR,Brazil,Brasilia,8511965,201103330,SA,.br,BRL,Real,55,#####-###,^(\d{8})$,"pt-BR,es,en,fr","SR,PE,BO,UY,GY,PY,GF,VE,CO,AR"
BS,Bahamas,Nassau,13940,301790,NA,.bs,BSD,Dollar,+1-242,,,en-BS,
BT,Bhutan,Thimphu,47000,699847,AS,.bt,BTN,Ngultrum,975,,,dz,"CN,IN"
BV,Bouvet Island,,49,0,AN,.bv,NOK,Krone,,,,,
BW,Botswana,Gaborone,600370,2029307,AF,.bw,BWP,Pula,267,,,"en-BW,tn-BW","ZW,ZA,NA"
BY,Belarus,Minsk,207600,9685000,EU,.by,BYR,Ruble,375,######,^(\d{6})$,"be,ru","PL,LT,UA,RU,LV"
BZ,Belize,Belmopan,22966,314522,NA,.bz,BZD,Dollar,501,,,"en-BZ,es","GT,MX"
CA,Canada,Ottawa,9984670,33679000,NA,.ca,CAD,Dollar,1,@#@ #@#,^([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ]) ?(\d[ABCEGHJKLMNPRSTVWXYZ]\d)$ ,"en-CA,fr-CA,iu",US
CC,Cocos Islands,West Island,14,628,AS,.cc,AUD,Dollar,61,,,"ms-CC,en",
CD,Democratic Republic of the Congo,Kinshasa,2345410,70916439,AF,.cd,CDF,Franc,243,,,"fr-CD,ln,kg","TZ,CF,SS,RW,ZM,BI,UG,CG,AO"
CF,Central African Republic,Bangui,622984,4844927,AF,.cf,XAF,Franc,236,,,"fr-CF,sg,ln,kg","TD,SD,CD,SS,CM,CG"
CG,Republic of the Congo,Brazzaville,342000,3039126,AF,.cg,XAF,Franc,242,,,"fr-CG,kg,ln-CG","CF,GA,CD,CM,AO"
CH,Switzerland,Berne,41290,7581000,EU,.ch,CHF,Franc,41,####,^(\d{4})$,"de-CH,fr-CH,it-CH,rm","DE,IT,LI,FR,AT"
CI,Ivory Coast,Yamoussoukro,322460,21058798,AF,.ci,XOF,Franc,225,,,fr-CI,"LR,GH,GN,BF,ML"
CK,Cook Islands,Avarua,240,21388,OC,.ck,NZD,Dollar,682,,,"en-CK,mi",
CL,Chile,Santiago,756950,16746491,SA,.cl,CLP,Peso,56,#######,^(\d{7})$,es-CL,"PE,BO,AR"
CM,Cameroon,Yaounde,475440,19294149,AF,.cm,XAF,Franc,237,,,"en-CM,fr-CM","TD,CF,GA,GQ,CG,NG"
CN,China,Beijing,9596960,1330044000,AS,.cn,CNY,Yuan Renminbi,86,######,^(\d{6})$,"zh-CN,yue,wuu,dta,ug,za","LA,BT,TJ,KZ,MN,AF,NP,MM,KG,PK,KP,RU,VN,IN"
CO,Colombia,Bogota,1138910,44205293,SA,.co,COP,Peso,57,,,es-CO,"EC,PE,PA,BR,VE"
CR,Costa Rica,San Jose,51100,4516220,NA,.cr,CRC,Colon,506,####,^(\d{4})$,"es-CR,en","PA,NI"
CU,Cuba,Havana,110860,11423000,NA,.cu,CUP,Peso,53,CP #####,^(?:CP)*(\d{5})$,es-CU,US
CV,Cape Verde,Praia,4033,508659,AF,.cv,CVE,Escudo,238,####,^(\d{4})$,pt-CV,
CW,Curacao, Willemstad,444,141766,NA,.cw,ANG,Guilder,599,,,"nl,pap",
CX,Christmas Island,Flying Fish Cove,135,1500,AS,.cx,AUD,Dollar,61,####,^(\d{4})$,"en,zh,ms-CC",
CY,Cyprus,Nicosia,9250,1102677,EU,.cy,EUR,Euro,357,####,^(\d{4})$,"el-CY,tr-CY,en",
CZ,Czech Republic,Prague,78866,10476000,EU,.cz,CZK,Koruna,420,### ##,^(\d{5})$,"cs,sk","PL,DE,SK,AT"
DE,Germany,Berlin,357021,81802257,EU,.de,EUR,Euro,49,#####,^(\d{5})$,de,"CH,PL,NL,DK,BE,CZ,LU,FR,AT"
DJ,Djibouti,Djibouti,23000,740528,AF,.dj,DJF,Franc,253,,,"fr-DJ,ar,so-DJ,aa","ER,ET,SO"
DK,Denmark,Copenhagen,43094,5484000,EU,.dk,DKK,Krone,45,####,^(\d{4})$,"da-DK,en,fo,de-DK",DE
DM,Dominica,Roseau,754,72813,NA,.dm,XCD,Dollar,+1-767,,,en-DM,
DO,Dominican Republic,Santo Domingo,48730,9823821,NA,.do,DOP,Peso,+1-809 and 1-829,#####,^(\d{5})$,es-DO,HT
DZ,Algeria,Algiers,2381740,34586184,AF,.dz,DZD,Dinar,213,#####,^(\d{5})$,ar-DZ,"NE,EH,LY,MR,TN,MA,ML"
EC,Ecuador,Quito,283560,14790608,SA,.ec,USD,Dollar,593,@####@,^([a-zA-Z]\d{4}[a-zA-Z])$,es-EC,"PE,CO"
EE,Estonia,Tallinn,45226,1291170,EU,.ee,EUR,Euro,372,#####,^(\d{5})$,"et,ru","RU,LV"
EG,Egypt,Cairo,1001450,80471869,AF,.eg,EGP,Pound,20,#####,^(\d{5})$,"ar-EG,en,fr","LY,SD,IL"
EH,Western Sahara,El-Aaiun,266000,273008,AF,.eh,MAD,Dirham,212,,,"ar,mey","DZ,MR,MA"
ER,Eritrea,Asmara,121320,5792984,AF,.er,ERN,Nakfa,291,,,"aa-ER,ar,tig,kun,ti-ER","ET,SD,DJ"
ES,Spain,Madrid,504782,46505963,EU,.es,EUR,Euro,34,#####,^(\d{5})$,"es-ES,ca,gl,eu,oc","AD,PT,GI,FR,MA"
ET,Ethiopia,Addis Ababa,1127127,88013491,AF,.et,ETB,Birr,251,####,^(\d{4})$,"am,en-ET,om-ET,ti-ET,so-ET,sid","ER,KE,SD,SS,SO,DJ"
FI,Finland,Helsinki,337030,5244000,EU,.fi,EUR,Euro,358,#####,^(?:FI)*(\d{5})$,"fi-FI,sv-FI,smn","NO,RU,SE"
FJ,Fiji,Suva,18270,875983,OC,.fj,FJD,Dollar,679,,,"en-FJ,fj",
FK,Falkland Islands,Stanley,12173,2638,SA,.fk,FKP,Pound,500,,,en-FK,
FM,Micronesia,Palikir,702,107708,OC,.fm,USD,Dollar,691,#####,^(\d{5})$,"en-FM,chk,pon,yap,kos,uli,woe,nkr,kpg",
FO,Faroe Islands,Torshavn,1399,48228,EU,.fo,DKK,Krone,298,FO-###,^(?:FO)*(\d{3})$,"fo,da-FO",
FR,France,Paris,547030,64768389,EU,.fr,EUR,Euro,33,#####,^(\d{5})$,"fr-FR,frp,br,co,ca,eu,oc","CH,DE,BE,LU,IT,AD,MC,ES"
GA,Gabon,Libreville,267667,1545255,AF,.ga,XAF,Franc,241,,,fr-GA,"CM,GQ,CG"
GB,United Kingdom,London,244820,62348447,EU,.uk,GBP,Pound,44,@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA,^(([A-Z]\d{2}[A-Z]{2})|([A-Z]\d{3}[A-Z]{2})|([A-Z]{2}\d{2}[A-Z]{2})|([A-Z]{2}\d{3}[A-Z]{2})|([A-Z]\d[A-Z]\d[A-Z]{2})|([A-Z]{2}\d[A-Z]\d[A-Z]{2})|(GIR0AA))$,"en-GB,cy-GB,gd",IE
GD,Grenada,St. George's,344,107818,NA,.gd,XCD,Dollar,+1-473,,,en-GD,
GE,Georgia,Tbilisi,69700,4630000,AS,.ge,GEL,Lari,995,####,^(\d{4})$,"ka,ru,hy,az","AM,AZ,TR,RU"
GF,French Guiana,Cayenne,91000,195506,SA,.gf,EUR,Euro,594,#####,^((97|98)3\d{2})$,fr-GF,"SR,BR"
GG,Guernsey,St Peter Port,78,65228,EU,.gg,GBP,Pound,+44-1481,@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA,^(([A-Z]\d{2}[A-Z]{2})|([A-Z]\d{3}[A-Z]{2})|([A-Z]{2}\d{2}[A-Z]{2})|([A-Z]{2}\d{3}[A-Z]{2})|([A-Z]\d[A-Z]\d[A-Z]{2})|([A-Z]{2}\d[A-Z]\d[A-Z]{2})|(GIR0AA))$,"en,fr",
GH,Ghana,Accra,239460,24339838,AF,.gh,GHS,Cedi,233,,,"en-GH,ak,ee,tw","CI,TG,BF"
GI,Gibraltar,Gibraltar,6.5,27884,EU,.gi,GIP,Pound,350,,,"en-GI,es,it,pt",ES
GL,Greenland,Nuuk,2166086,56375,NA,.gl,DKK,Krone,299,####,^(\d{4})$,"kl,da-GL,en",
GM,Gambia,Banjul,11300,1593256,AF,.gm,GMD,Dalasi,220,,,"en-GM,mnk,wof,wo,ff",SN
GN,Guinea,Conakry,245857,10324025,AF,.gn,GNF,Franc,224,,,fr-GN,"LR,SN,SL,CI,GW,ML"
GP,Guadeloupe,Basse-Terre,1780,443000,NA,.gp,EUR,Euro,590,#####,^((97|98)\d{3})$,fr-GP,AN
GQ,Equatorial Guinea,Malabo,28051,1014999,AF,.gq,XAF,Franc,240,,,"es-GQ,fr","GA,CM"
GR,Greece,Athens,131940,11000000,EU,.gr,EUR,Euro,30,### ##,^(\d{5})$,"el-GR,en,fr","AL,MK,TR,BG"
GS,South Georgia and the South Sandwich Islands,Grytviken,3903,30,AN,.gs,GBP,Pound,,,,en,
GT,Guatemala,Guatemala City,108890,13550440,NA,.gt,GTQ,Quetzal,502,#####,^(\d{5})$,es-GT,"MX,HN,BZ,SV"
GU,Guam,Hagatna,549,159358,OC,.gu,USD,Dollar,+1-671,969##,^(969\d{2})$,"en-GU,ch-GU",
GW,Guinea-Bissau,Bissau,36120,1565126,AF,.gw,XOF,Franc,245,####,^(\d{4})$,"pt-GW,pov","SN,GN"
GY,Guyana,Georgetown,214970,748486,SA,.gy,GYD,Dollar,592,,,en-GY,"SR,BR,VE"
HK,Hong Kong,Hong Kong,1092,6898686,AS,.hk,HKD,Dollar,852,,,"zh-HK,yue,zh,en",
HM,Heard Island and McDonald Islands,,412,0,AN,.hm,AUD,Dollar, ,,,,
HN,Honduras,Tegucigalpa,112090,7989415,NA,.hn,HNL,Lempira,504,@@####,^([A-Z]{2}\d{4})$,es-HN,"GT,NI,SV"
HR,Croatia,Zagreb,56542,4491000,EU,.hr,HRK,Kuna,385,#####,^(?:HR)*(\d{5})$,"hr-HR,sr","HU,SI,CS,BA,ME,RS"
HT,Haiti,Port-au-Prince,27750,9648924,NA,.ht,HTG,Gourde,509,HT####,^(?:HT)*(\d{4})$,"ht,fr-HT",DO
HU,Hungary,Budapest,93030,9982000,EU,.hu,HUF,Forint,36,####,^(\d{4})$,hu-HU,"SK,SI,RO,UA,CS,HR,AT,RS"
ID,Indonesia,Jakarta,1919440,242968342,AS,.id,IDR,Rupiah,62,#####,^(\d{5})$,"id,en,nl,jv","PG,TL,MY"
IE,Ireland,Dublin,70280,4622917,EU,.ie,EUR,Euro,353,,,"en-IE,ga-IE",GB
IL,Israel,Jerusalem,20770,7353985,AS,.il,ILS,Shekel,972,#####,^(\d{5})$,"he,ar-IL,en-IL,","SY,JO,LB,EG,PS"
IM,Isle of Man,"Douglas, Isle of Man",572,75049,EU,.im,GBP,Pound,+44-1624,@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA,^(([A-Z]\d{2}[A-Z]{2})|([A-Z]\d{3}[A-Z]{2})|([A-Z]{2}\d{2}[A-Z]{2})|([A-Z]{2}\d{3}[A-Z]{2})|([A-Z]\d[A-Z]\d[A-Z]{2})|([A-Z]{2}\d[A-Z]\d[A-Z]{2})|(GIR0AA))$,"en,gv",
IN,India,New Delhi,3287590,1173108018,AS,.in,INR,Rupee,91,######,^(\d{6})$,"en-IN,hi,bn,te,mr,ta,ur,gu,kn,ml,or,pa,as,bh,sat,ks,ne,sd,kok,doi,mni,sit,sa,fr,lus,inc","CN,NP,MM,BT,PK,BD"
IO,British Indian Ocean Territory,Diego Garcia,60,4000,AS,.io,USD,Dollar,246,,,en-IO,
IQ,Iraq,Baghdad,437072,29671605,AS,.iq,IQD,Dinar,964,#####,^(\d{5})$,"ar-IQ,ku,hy","SY,SA,IR,JO,TR,KW"
IR,Iran,Tehran,1648000,76923300,AS,.ir,IRR,Rial,98,##########,^(\d{10})$,"fa-IR,ku","TM,AF,IQ,AM,PK,AZ,TR"
IS,Iceland,Reykjavik,103000,308910,EU,.is,ISK,Krona,354,###,^(\d{3})$,"is,en,de,da,sv,no",
IT,Italy,Rome,301230,60340328,EU,.it,EUR,Euro,39,#####,^(\d{5})$,"it-IT,de-IT,fr-IT,sc,ca,co,sl","CH,VA,SI,SM,FR,AT"
JE,Jersey,Saint Helier,116,90812,EU,.je,GBP,Pound,+44-1534,@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA,^(([A-Z]\d{2}[A-Z]{2})|([A-Z]\d{3}[A-Z]{2})|([A-Z]{2}\d{2}[A-Z]{2})|([A-Z]{2}\d{3}[A-Z]{2})|([A-Z]\d[A-Z]\d[A-Z]{2})|([A-Z]{2}\d[A-Z]\d[A-Z]{2})|(GIR0AA))$,"en,pt",
JM,Jamaica,Kingston,10991,2847232,NA,.jm,JMD,Dollar,+1-876,,,en-JM,
JO,Jordan,Amman,92300,6407085,AS,.jo,JOD,Dinar,962,#####,^(\d{5})$,"ar-JO,en","SY,SA,IQ,IL,PS"
JP,Japan,Tokyo,377835,127288000,AS,.jp,JPY,Yen,81,###-####,^(\d{7})$,ja,
KE,Kenya,Nairobi,582650,40046566,AF,.ke,KES,Shilling,254,#####,^(\d{5})$,"en-KE,sw-KE","ET,TZ,SS,SO,UG"
KG,Kyrgyzstan,Bishkek,198500,5508626,AS,.kg,KGS,Som,996,######,^(\d{6})$,"ky,uz,ru","CN,TJ,UZ,KZ"
KH,Cambodia,Phnom Penh,181040,14453680,AS,.kh,KHR,Riels,855,#####,^(\d{5})$,"km,fr,en","LA,TH,VN"
KI,Kiribati,Tarawa,811,92533,OC,.ki,AUD,Dollar,686,,,"en-KI,gil",
KM,Comoros,Moroni,2170,773407,AF,.km,KMF,Franc,269,,,"ar,fr-KM",
KN,Saint Kitts and Nevis,Basseterre,261,51134,NA,.kn,XCD,Dollar,+1-869,,,en-KN,
KP,North Korea,Pyongyang,120540,22912177,AS,.kp,KPW,Won,850,###-###,^(\d{6})$,ko-KP,"CN,KR,RU"
KR,South Korea,Seoul,98480,48422644,AS,.kr,KRW,Won,82,SEOUL ###-###,^(?:SEOUL)*(\d{6})$,"ko-KR,en",KP
XK,Kosovo,Pristina,10908,1800000,EU,,EUR,Euro,,,,"sq,sr","RS,AL,MK,ME"
KW,Kuwait,Kuwait City,17820,2789132,AS,.kw,KWD,Dinar,965,#####,^(\d{5})$,"ar-KW,en","SA,IQ"
KY,Cayman Islands,George Town,262,44270,NA,.ky,KYD,Dollar,+1-345,,,en-KY,
KZ,Kazakhstan,Astana,2717300,15340000,AS,.kz,KZT,Tenge,7,######,^(\d{6})$,"kk,ru","TM,CN,KG,UZ,RU"
LA,Laos,Vientiane,236800,6368162,AS,.la,LAK,Kip,856,#####,^(\d{5})$,"lo,fr,en","CN,MM,KH,TH,VN"
LB,Lebanon,Beirut,10400,4125247,AS,.lb,LBP,Pound,961,#### ####|####,^(\d{4}(\d{4})?)$,"ar-LB,fr-LB,en,hy","SY,IL"
LC,Saint Lucia,Castries,616,160922,NA,.lc,XCD,Dollar,+1-758,,,en-LC,
LI,Liechtenstein,Vaduz,160,35000,EU,.li,CHF,Franc,423,####,^(\d{4})$,de-LI,"CH,AT"
LK,Sri Lanka,Colombo,65610,21513990,AS,.lk,LKR,Rupee,94,#####,^(\d{5})$,"si,ta,en",
LR,Liberia,Monrovia,111370,3685076,AF,.lr,LRD,Dollar,231,####,^(\d{4})$,en-LR,"SL,CI,GN"
LS,Lesotho,Maseru,30355,1919552,AF,.ls,LSL,Loti,266,###,^(\d{3})$,"en-LS,st,zu,xh",ZA
LT,Lithuania,Vilnius,65200,3565000,EU,.lt,LTL,Litas,370,LT-#####,^(?:LT)*(\d{5})$,"lt,ru,pl","PL,BY,RU,LV"
LU,Luxembourg,Luxembourg,2586,497538,EU,.lu,EUR,Euro,352,L-####,^(\d{4})$,"lb,de-LU,fr-LU","DE,BE,FR"
LV,Latvia,Riga,64589,2217969,EU,.lv,EUR,Euro,371,LV-####,^(?:LV)*(\d{4})$,"lv,ru,lt","LT,EE,BY,RU"
LY,Libya,Tripolis,1759540,6461454,AF,.ly,LYD,Dinar,218,,,"ar-LY,it,en","TD,NE,DZ,SD,TN,EG"
MA,Morocco,Rabat,446550,31627428,AF,.ma,MAD,Dirham,212,#####,^(\d{5})$,"ar-MA,fr","DZ,EH,ES"
MC,Monaco,Monaco,1.95,32965,EU,.mc,EUR,Euro,377,#####,^(\d{5})$,"fr-MC,en,it",FR
MD,Moldova,Chisinau,33843,4324000,EU,.md,MDL,Leu,373,MD-####,^(?:MD)*(\d{4})$,"ro,ru,gag,tr","RO,UA"
ME,Montenegro,Podgorica,14026,666730,EU,.me,EUR,Euro,382,#####,^(\d{5})$,"sr,hu,bs,sq,hr,rom","AL,HR,BA,RS,XK"
MF,Saint Martin,Marigot,53,35925,NA,.gp,EUR,Euro,590,### ###,,fr,SX
MG,Madagascar,Antananarivo,587040,21281844,AF,.mg,MGA,Ariary,261,###,^(\d{3})$,"fr-MG,mg",
MH,Marshall Islands,Majuro,181.3,65859,OC,.mh,USD,Dollar,692,,,"mh,en-MH",
MK,Macedonia,Skopje,25333,2062294,EU,.mk,MKD,Denar,389,####,^(\d{4})$,"mk,sq,tr,rmm,sr","AL,GR,CS,BG,RS,XK"
ML,Mali,Bamako,1240000,13796354,AF,.ml,XOF,Franc,223,,,"fr-ML,bm","SN,NE,DZ,CI,GN,MR,BF"
MM,Myanmar,Nay Pyi Taw,678500,53414374,AS,.mm,MMK,Kyat,95,#####,^(\d{5})$,my,"CN,LA,TH,BD,IN"
MN,Mongolia,Ulan Bator,1565000,3086918,AS,.mn,MNT,Tugrik,976,######,^(\d{6})$,"mn,ru","CN,RU"
MO,Macao,Macao,254,449198,AS,.mo,MOP,Pataca,853,,,"zh,zh-MO,pt",
MP,Northern Mariana Islands,Saipan,477,53883,OC,.mp,USD,Dollar,+1-670,,,"fil,tl,zh,ch-MP,en-MP",
MQ,Martinique,Fort-de-France,1100,432900,NA,.mq,EUR,Euro,596,#####,^(\d{5})$,fr-MQ,
MR,Mauritania,Nouakchott,1030700,3205060,AF,.mr,MRO,Ouguiya,222,,,"ar-MR,fuc,snk,fr,mey,wo","SN,DZ,EH,ML"
MS,Montserrat,Plymouth,102,9341,NA,.ms,XCD,Dollar,+1-664,,,en-MS,
MT,Malta,Valletta,316,403000,EU,.mt,EUR,Euro,356,@@@ ###|@@@ ##,^([A-Z]{3}\d{2}\d?)$,"mt,en-MT",
MU,Mauritius,Port Louis,2040,1294104,AF,.mu,MUR,Rupee,230,,,"en-MU,bho,fr",
MV,Maldives,Male,300,395650,AS,.mv,MVR,Rufiyaa,960,#####,^(\d{5})$,"dv,en",
MW,Malawi,Lilongwe,118480,15447500,AF,.mw,MWK,Kwacha,265,,,"ny,yao,tum,swk","TZ,MZ,ZM"
MX,Mexico,Mexico City,1972550,112468855,NA,.mx,MXN,Peso,52,#####,^(\d{5})$,es-MX,"GT,US,BZ"
MY,Malaysia,Kuala Lumpur,329750,28274729,AS,.my,MYR,Ringgit,60,#####,^(\d{5})$,"ms-MY,en,zh,ta,te,ml,pa,th","BN,TH,ID"
MZ,Mozambique,Maputo,801590,22061451,AF,.mz,MZN,Metical,258,####,^(\d{4})$,"pt-MZ,vmw","ZW,TZ,SZ,ZA,ZM,MW"
NA,Namibia,Windhoek,825418,2128471,AF,.na,NAD,Dollar,264,,,"en-NA,af,de,hz,naq","ZA,BW,ZM,AO"
NC,New Caledonia,Noumea,19060,216494,OC,.nc,XPF,Franc,687,#####,^(\d{5})$,fr-NC,
NE,Niger,Niamey,1267000,15878271,AF,.ne,XOF,Franc,227,####,^(\d{4})$,"fr-NE,ha,kr,dje","TD,BJ,DZ,LY,BF,NG,ML"
NF,Norfolk Island,Kingston,34.6,1828,OC,.nf,AUD,Dollar,672,####,^(\d{4})$,en-NF,
NG,Nigeria,Abuja,923768,154000000,AF,.ng,NGN,Naira,234,######,^(\d{6})$,"en-NG,ha,yo,ig,ff","TD,NE,BJ,CM"
NI,Nicaragua,Managua,129494,5995928,NA,.ni,NIO,Cordoba,505,###-###-#,^(\d{7})$,"es-NI,en","CR,HN"
NL,Netherlands,Amsterdam,41526,16645000,EU,.nl,EUR,Euro,31,#### @@,^(\d{4}[A-Z]{2})$,"nl-NL,fy-NL","DE,BE"
NO,Norway,Oslo,324220,5009150,EU,.no,NOK,Krone,47,####,^(\d{4})$,"no,nb,nn,se,fi","FI,RU,SE"
NP,Nepal,Kathmandu,140800,28951852,AS,.np,NPR,Rupee,977,#####,^(\d{5})$,"ne,en","CN,IN"
NR,Nauru,Yaren,21,10065,OC,.nr,AUD,Dollar,674,,,"na,en-NR",
NU,Niue,Alofi,260,2166,OC,.nu,NZD,Dollar,683,,,"niu,en-NU",
NZ,New Zealand,Wellington,268680,4252277,OC,.nz,NZD,Dollar,64,####,^(\d{4})$,"en-NZ,mi",
OM,Oman,Muscat,212460,2967717,AS,.om,OMR,Rial,968,###,^(\d{3})$,"ar-OM,en,bal,ur","SA,YE,AE"
PA,Panama,Panama City,78200,3410676,NA,.pa,PAB,Balboa,507,,,"es-PA,en","CR,CO"
PE,Peru,Lima,1285220,29907003,SA,.pe,PEN,Sol,51,,,"es-PE,qu,ay","EC,CL,BO,BR,CO"
PF,French Polynesia,Papeete,4167,270485,OC,.pf,XPF,Franc,689,#####,^((97|98)7\d{2})$,"fr-PF,ty",
PG,Papua New Guinea,Port Moresby,462840,6064515,OC,.pg,PGK,Kina,675,###,^(\d{3})$,"en-PG,ho,meu,tpi",ID
PH,Philippines,Manila,300000,99900177,AS,.ph,PHP,Peso,63,####,^(\d{4})$,"tl,en-PH,fil",
PK,Pakistan,Islamabad,803940,184404791,AS,.pk,PKR,Rupee,92,#####,^(\d{5})$,"ur-PK,en-PK,pa,sd,ps,brh","CN,AF,IR,IN"
PL,Poland,Warsaw,312685,38500000,EU,.pl,PLN,Zloty,48,##-###,^(\d{5})$,pl,"DE,LT,SK,CZ,BY,UA,RU"
PM,Saint Pierre and Miquelon,Saint-Pierre,242,7012,NA,.pm,EUR,Euro,508,#####,^(97500)$,fr-PM,
PN,Pitcairn,Adamstown,47,46,OC,.pn,NZD,Dollar,870,,,en-PN,
PR,Puerto Rico,San Juan,9104,3916632,NA,.pr,USD,Dollar,+1-787 and 1-939,#####-####,^(\d{9})$,"en-PR,es-PR",
PS,Palestinian Territory,East Jerusalem,5970,3800000,AS,.ps,ILS,Shekel,970,,,ar-PS,"JO,IL"
PT,Portugal,Lisbon,92391,10676000,EU,.pt,EUR,Euro,351,####-###,^(\d{7})$,"pt-PT,mwl",ES
PW,Palau,Melekeok,458,19907,OC,.pw,USD,Dollar,680,96940,^(96940)$,"pau,sov,en-PW,tox,ja,fil,zh",
PY,Paraguay,Asuncion,406750,6375830,SA,.py,PYG,Guarani,595,####,^(\d{4})$,"es-PY,gn","BO,BR,AR"
QA,Qatar,Doha,11437,840926,AS,.qa,QAR,Rial,974,,,"ar-QA,es",SA
RE,Reunion,Saint-Denis,2517,776948,AF,.re,EUR,Euro,262,#####,^((97|98)(4|7|8)\d{2})$,fr-RE,
RO,Romania,Bucharest,237500,21959278,EU,.ro,RON,Leu,40,######,^(\d{6})$,"ro,hu,rom","MD,HU,UA,CS,BG,RS"
RS,Serbia,Belgrade,88361,7344847,EU,.rs,RSD,Dinar,381,######,^(\d{6})$,"sr,hu,bs,rom","AL,HU,MK,RO,HR,BA,BG,ME,XK"
RU,Russia,Moscow,17100000,140702000,EU,.ru,RUB,Ruble,7,######,^(\d{6})$,"ru,tt,xal,cau,ady,kv,ce,tyv,cv,udm,tut,mns,bua,myv,mdf,chm,ba,inh,tut,kbd,krc,ava,sah,nog","GE,CN,BY,UA,KZ,LV,PL,EE,LT,FI,MN,NO,AZ,KP"
RW,Rwanda,Kigali,26338,11055976,AF,.rw,RWF,Franc,250,,,"rw,en-RW,fr-RW,sw","TZ,CD,BI,UG"
SA,Saudi Arabia,Riyadh,1960582,25731776,AS,.sa,SAR,Rial,966,#####,^(\d{5})$,ar-SA,"QA,OM,IQ,YE,JO,AE,KW"
SB,Solomon Islands,Honiara,28450,559198,OC,.sb,SBD,Dollar,677,,,"en-SB,tpi",
SC,Seychelles,Victoria,455,88340,AF,.sc,SCR,Rupee,248,,,"en-SC,fr-SC",
SD,Sudan,Khartoum,1861484,35000000,AF,.sd,SDG,Pound,249,#####,^(\d{5})$,"ar-SD,en,fia","SS,TD,EG,ET,ER,LY,CF"
SS,South Sudan,Juba,644329,8260490,AF,,SSP,Pound,211,,,en,"CD,CF,ET,KE,SD,UG,"
SE,Sweden,Stockholm,449964,9555893,EU,.se,SEK,Krona,46,### ##,^(?:SE)*(\d{5})$,"sv-SE,se,sma,fi-SE","NO,FI"
SG,Singapore,Singapur,692.7,4701069,AS,.sg,SGD,Dollar,65,######,^(\d{6})$,"cmn,en-SG,ms-SG,ta-SG,zh-SG",
SH,Saint Helena,Jamestown,410,7460,AF,.sh,SHP,Pound,290,STHL 1ZZ,^(STHL1ZZ)$,en-SH,
SI,Slovenia,Ljubljana,20273,2007000,EU,.si,EUR,Euro,386,####,^(?:SI)*(\d{4})$,"sl,sh","HU,IT,HR,AT"
SJ,Svalbard and Jan Mayen,Longyearbyen,62049,2550,EU,.sj,NOK,Krone,47,,,"no,ru",
SK,Slovakia,Bratislava,48845,5455000,EU,.sk,EUR,Euro,421,### ##,^(\d{5})$,"sk,hu","PL,HU,CZ,UA,AT"
SL,Sierra Leone,Freetown,71740,5245695,AF,.sl,SLL,Leone,232,,,"en-SL,men,tem","LR,GN"
SM,San Marino,San Marino,61.2,31477,EU,.sm,EUR,Euro,378,4789#,^(4789\d)$,it-SM,IT
SN,Senegal,Dakar,196190,12323252,AF,.sn,XOF,Franc,221,#####,^(\d{5})$,"fr-SN,wo,fuc,mnk","GN,MR,GW,GM,ML"
SO,Somalia,Mogadishu,637657,10112453,AF,.so,SOS,Shilling,252,@@  #####,^([A-Z]{2}\d{5})$,"so-SO,ar-SO,it,en-SO","ET,KE,DJ"
SR,Suriname,Paramaribo,163270,492829,SA,.sr,SRD,Dollar,597,,,"nl-SR,en,srn,hns,jv","GY,BR,GF"
ST,Sao Tome and Principe,Sao Tome,1001,175808,AF,.st,STD,Dobra,239,,,pt-ST,
SV,El Salvador,San Salvador,21040,6052064,NA,.sv,USD,Dollar,503,CP ####,^(?:CP)*(\d{4})$,es-SV,"GT,HN"
SX,Sint Maarten,Philipsburg,34,37429,NA,.sx,ANG,Guilder,599,,,"nl,en",MF
SY,Syria,Damascus,185180,22198110,AS,.sy,SYP,Pound,963,,,"ar-SY,ku,hy,arc,fr,en","IQ,JO,IL,TR,LB"
SZ,Swaziland,Mbabane,17363,1354051,AF,.sz,SZL,Lilangeni,268,@###,^([A-Z]\d{3})$,"en-SZ,ss-SZ","ZA,MZ"
TC,Turks and Caicos Islands,Cockburn Town,430,20556,NA,.tc,USD,Dollar,+1-649,TKCA 1ZZ,^(TKCA 1ZZ)$,en-TC,
TD,Chad,N'Djamena,1284000,10543464,AF,.td,XAF,Franc,235,,,"fr-TD,ar-TD,sre","NE,LY,CF,SD,CM,NG"
TF,French Southern Territories,Port-aux-Francais,7829,140,AN,.tf,EUR,Euro  ,,,,fr,
TG,Togo,Lome,56785,6587239,AF,.tg,XOF,Franc,228,,,"fr-TG,ee,hna,kbp,dag,ha","BJ,GH,BF"
TH,Thailand,Bangkok,514000,67089500,AS,.th,THB,Baht,66,#####,^(\d{5})$,"th,en","LA,MM,KH,MY"
TJ,Tajikistan,Dushanbe,143100,7487489,AS,.tj,TJS,Somoni,992,######,^(\d{6})$,"tg,ru","CN,AF,KG,UZ"
TK,Tokelau,,10,1466,OC,.tk,NZD,Dollar,690,,,"tkl,en-TK",
TL,East Timor,Dili,15007,1154625,OC,.tl,USD,Dollar,670,,,"tet,pt-TL,id,en",ID
TM,Turkmenistan,Ashgabat,488100,4940916,AS,.tm,TMT,Manat,993,######,^(\d{6})$,"tk,ru,uz","AF,IR,UZ,KZ"
TN,Tunisia,Tunis,163610,10589025,AF,.tn,TND,Dinar,216,####,^(\d{4})$,"ar-TN,fr","DZ,LY"
TO,Tonga,Nuku'alofa,748,122580,OC,.to,TOP,Pa'anga,676,,,"to,en-TO",
TR,Turkey,Ankara,780580,77804122,AS,.tr,TRY,Lira,90,#####,^(\d{5})$,"tr-TR,ku,diq,az,av","SY,GE,IQ,IR,GR,AM,AZ,BG"
TT,Trinidad and Tobago,Port of Spain,5128,1228691,NA,.tt,TTD,Dollar,+1-868,,,"en-TT,hns,fr,es,zh",
TV,Tuvalu,Funafuti,26,10472,OC,.tv,AUD,Dollar,688,,,"tvl,en,sm,gil",
TW,Taiwan,Taipei,35980,22894384,AS,.tw,TWD,Dollar,886,#####,^(\d{5})$,"zh-TW,zh,nan,hak",
TZ,Tanzania,Dodoma,945087,41892895,AF,.tz,TZS,Shilling,255,,,"sw-TZ,en,ar","MZ,KE,CD,RW,ZM,BI,UG,MW"
UA,Ukraine,Kiev,603700,45415596,EU,.ua,UAH,Hryvnia,380,#####,^(\d{5})$,"uk,ru-UA,rom,pl,hu","PL,MD,HU,SK,BY,RO,RU"
UG,Uganda,Kampala,236040,33398682,AF,.ug,UGX,Shilling,256,,,"en-UG,lg,sw,ar","TZ,KE,SS,CD,RW"
UM,United States Minor Outlying Islands,,0,0,OC,.um,USD,Dollar ,1,,,en-UM,
US,United States,Washington,9629091,310232863,NA,.us,USD,Dollar,1,#####-####,^\d{5}(-\d{4})?$,"en-US,es-US,haw,fr","CA,MX,CU"
UY,Uruguay,Montevideo,176220,3477000,SA,.uy,UYU,Peso,598,#####,^(\d{5})$,es-UY,"BR,AR"
UZ,Uzbekistan,Tashkent,447400,27865738,AS,.uz,UZS,Som,998,######,^(\d{6})$,"uz,ru,tg","TM,AF,KG,TJ,KZ"
VA,Vatican,Vatican City,0.44,921,EU,.va,EUR,Euro,379,#####,^(\d{5})$,"la,it,fr",IT
VC,Saint Vincent and the Grenadines,Kingstown,389,104217,NA,.vc,XCD,Dollar,+1-784,,,"en-VC,fr",
VE,Venezuela,Caracas,912050,27223228,SA,.ve,VEF,Bolivar,58,####,^(\d{4})$,es-VE,"GY,BR,CO"
VG,British Virgin Islands,Road Town,153,21730,NA,.vg,USD,Dollar,+1-284,,,en-VG,
VI,U.S. Virgin Islands,Charlotte Amalie,352,108708,NA,.vi,USD,Dollar,+1-340,#####-####,^\d{5}(-\d{4})?$,en-VI,
VN,Vietnam,Hanoi,329560,89571130,AS,.vn,VND,Dong,84,######,^(\d{6})$,"vi,en,fr,zh,km","CN,LA,KH"
VU,Vanuatu,Port Vila,12200,221552,OC,.vu,VUV,Vatu,678,,,"bi,en-VU,fr-VU",
WF,Wallis and Futuna,Mata Utu,274,16025,OC,.wf,XPF,Franc,681,#####,^(986\d{2})$,"wls,fud,fr-WF",
WS,Samoa,Apia,2944,192001,OC,.ws,WST,Tala,685,,,"sm,en-WS",
YE,Yemen,Sanaa,527970,23495361,AS,.ye,YER,Rial,967,,,ar-YE,"SA,OM"
YT,Mayotte,Mamoudzou,374,159042,AF,.yt,EUR,Euro,262,#####,^(\d{5})$,fr-YT,
ZA,South Africa,Pretoria,1219912,49000000,AF,.za,ZAR,Rand,27,####,^(\d{4})$,"zu,xh,af,nso,en-ZA,tn,st,ts,ss,ve,nr","ZW,SZ,MZ,BW,NA,LS"
ZM,Zambia,Lusaka,752614,13460305,AF,.zm,ZMW,Kwacha,260,#####,^(\d{5})$,"en-ZM,bem,loz,lun,lue,ny,toi","ZW,TZ,MZ,CD,NA,MW,AO"
ZW,Zimbabwe,Harare,390580,11651858,AF,.zw,ZWL,Dollar,263,,,"en-ZW,sn,nr,nd","ZA,MZ,BW,ZM"
CS,Serbia and Montenegro,Belgrade,102350,10829175,EU,.cs,RSD,Dinar,381,#####,^(\d{5})$,"cu,hu,sq,sr","AL,HU,MK,RO,HR,BA,BG"
AN,Netherlands Antilles,Willemstad,960,136197,NA,.an,ANG,Guilder,599,,,"nl-AN,en,es",GP"""
        fp = StringIO.StringIO(text)
        rows = list(csv.reader(fp))
        # sort by country name
        rows.sort(key=lambda row: row[1])

        # delete existing places before inserting new ones
        self.db(self.db.places).delete()
        for i, row in enumerate(rows):
            # remove surrounding text
            row = [e.strip() for e in row]
            record = dict(zip(self.fields, row))
            # convert numeric fields to proper type
            for field in self.numeric_fields:
                try:
                    value = int(record[field])
                except ValueError:
                    value = float(record[field])
                record[field] = value
            # add country_id for ordering on GAE, which does not use sequential ID's
            record['country_id'] = i + 1
            record['national_flag'] = URL(c='static', f='images/flags/%s.png' % record['iso'].lower())
            self.db.places.insert(**record)
