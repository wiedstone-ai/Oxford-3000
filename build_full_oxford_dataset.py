import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import sqlite3
import eng_to_ipa as ipa
from parse_oxford import parsed

# Load oxford3000_examples.csv
import csv
examples_map = {}
with open('oxford3000_examples.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['Word'].lower().strip()
        ex = row['Example Sentence'].strip()
        if w and ex:
            examples_map[w] = ex

# Curated example sentences for words not in oxford3000_examples.csv
curated_sentences = {
    'a': 'She has a dog and two cats.',
    'a, an': 'An apple a day keeps the doctor away.',
    'administration': 'The university administration announced a new policy.',
    'agenda': 'What is the first item on today’s meeting agenda?',
    'ah': 'Ah, now I understand what you mean!',
    'airline': 'Which airline are you flying with to London?',
    'album': 'Their new music album was released yesterday.',
    'ambitious': 'She is an ambitious student who wants to be a doctor.',
    'announcement': 'The principal made an important announcement this morning.',
    'any more': 'I don’t want to talk about this any more.',
    'app': 'You can download the mobile app from the store.',
    'architect': 'The famous architect designed this modern building.',
    'architecture': 'Rome is famous for its classical architecture.',
    'assess': 'The test is designed to assess your English skills.',
    'assessment': 'Continuous assessment helps track student progress.',
    'assignment': 'Please submit your homework assignment by Friday.',
    'athlete': 'He trained hard to become a professional athlete.',
    'banana': 'He ate a ripe yellow banana for breakfast.',
    'baseball': 'They enjoy playing baseball in the afternoon.',
    'basketball': 'Basketball is very popular among teenagers.',
    'bean': 'We planted green beans in the garden.',
    'bee': 'A bee was buzzing around the garden flowers.',
    'beg': 'The poor man begged for food on the street.',
    'behaviour': 'His good behaviour was praised by the teacher.',
    'being': 'Thank you for being such a wonderful friend.',
    'blog': 'She writes a weekly blog about travel and food.',
    'bond': 'There is a strong bond between the mother and child.',
    'bride': 'The bride looked beautiful in her white wedding dress.',
    'cafe': 'Let’s meet at the cafe for a cup of coffee.',
    'campus': 'The new library is located in the center of the campus.',
    'can': 'Can you speak English fluently?',
    'cartoon': 'Children love watching animated cartoons on Saturday morning.',
    'celebrity': 'The film celebrity arrived at the red carpet.',
    'champion': 'Our school team became the regional champion.',
    'chef': 'The head chef prepared a special dinner for the guests.',
    'childhood': 'I spent most of my childhood in a small village.',
    'cite': 'Be sure to cite all your sources in the research paper.',
    'classical': 'She enjoys listening to classical music while studying.',
    'clause': 'A complex sentence contains an independent and a dependent clause.',
    'close': 'Please close the door when you leave the room.',
    'clue': 'The detective searched the room for any possible clues.',
    'coach': 'Our football coach encouraged us to do our best.',
    'competitor': 'The company launched a new product to beat its competitors.',
    'component': 'Hardware and software are the two main components of a computer.',
    'consistent': 'Consistent practice is the key to mastering a language.',
    'consume': 'Athletes need to consume enough water during training.',
    'convinced': 'I am convinced that hard work leads to success.',
    'corporate': 'She works in the corporate headquarters in Jakarta.',
    'costume': 'The children wore colorful costumes for Halloween.',
    'creation': 'The museum celebrates the creation of modern art.',
    'creative': 'She has many creative ideas for the school project.',
    'crew': 'The flight crew welcomed the passengers aboard the plane.',
    'critic': 'The film received glowing reviews from movie critics.',
    'currency': 'The official currency of Indonesia is the Rupiah.',
    'dad': 'My dad taught me how to ride a bicycle.',
    'decent': 'He earns a decent salary from his new job.',
    'delicious': 'The food at the local restaurant was delicious.',
    'designer': 'She is a talented fashion designer.',
    'destination': 'Bali is a top tourist destination in the world.',
    'detect': 'The device can detect smoke and warn us of fire.',
    'detective': 'The police detective solved the difficult mystery.',
    'dialogue': 'The actors practiced their dialogue before shooting.',
    'distribution': 'The distribution of books to remote schools has begun.',
    'documentary': 'We watched an interesting documentary about nature.',
    'donate': 'Many people donated money to the disaster victims.',
    'download': 'You can download the PDF file to your phone.',
    'drawing': 'Her drawing of the mountain won first prize.',
    'earthquake': 'A strong earthquake shook the city last night.',
    'edit': 'Please edit your essay before turning it in.',
    'educational': 'Visiting the science museum is a fun and educational trip.',
    'efficient': 'Using public transport is an efficient way to travel.',
    'elephant': 'The African elephant is the largest living land mammal.',
    'enhance': 'Reading English books helps enhance your vocabulary.',
    'episode': 'Have you seen the latest episode of that TV series?',
    'ethical': 'Doctors must follow strict ethical guidelines.',
    'evaluate': 'The teacher will evaluate our performance next week.',
    'everyday': 'English is very useful for everyday communication.',
    'expedition': 'The scientists embarked on an expedition to the Arctic.',
    'exploration': 'Space exploration has revealed many secrets of the universe.',
    'external': 'The external walls of the house were painted white.',
    'facility': 'Our school has excellent sports facilities and science labs.',
    'fantastic': 'We had a fantastic time on our vacation in Yogyakarta.',
    'fascinating': 'The history of ancient civilizations is truly fascinating.',
    'favour': 'Could you please do me a small favour?',
    'favourite': 'Blue is my favourite colour.',
    'feedback': 'Constructive feedback helps students improve their writing.',
    'fiction': 'She loves reading historical fiction novels.',
    'finding': 'The research findings were published in a scientific journal.',
    'firstly': 'Firstly, we need to gather all the required materials.',
    'five': 'There are five working days in a week.',
    'fixed': 'The meeting was set for a fixed date next month.',
    'flexible': 'My working hours are flexible, so I can work from home.',
    'flu': 'He stayed home from school because he had the flu.',
    'flying': 'She has always been afraid of flying in airplanes.',
    'folding': 'We brought folding chairs for the outdoor picnic.',
    'folk': 'They played traditional folk songs on acoustic instruments.',
    'former': 'The former president gave a speech at the conference.',
    'fortunately': 'Fortunately, the rain stopped just in time for the match.',
    'forty': 'My father celebrated his fortieth birthday yesterday.',
    'frame': 'She bought a wooden frame for her family photograph.',
    'frequency': 'The frequency of bus departures increases during rush hour.',
    'friday': 'We usually go out for dinner on Friday evening.',
    'fridge': 'Please put the milk back into the fridge.',
    'frog': 'A small green frog jumped into the pond.',
    'fry': 'Fry the onions in hot oil until they turn golden brown.',
    'funding': 'The university received government funding for medical research.',
    'furthermore': 'The project is affordable; furthermore, it will benefit many people.',
    'gallery': 'We visited the modern art gallery on Sunday.',
    'gang': 'The police arrested members of a local street gang.',
    'genre': 'Science fiction is my favourite book genre.',
    'ghost': 'Do you believe in ghosts and haunted houses?',
    'golf': 'He plays golf with his business partners on weekends.',
    'graduate': 'She will graduate from university next summer.',
    'guitar': 'He learned to play acoustic guitar when he was twelve.',
    'gun': 'Police officers are trained to use a gun responsibly.',
    'guy': 'He is a friendly guy who gets along with everyone.',
    'gym': 'I go to the school gym after class to exercise.',
    'happily': 'The children played happily in the playground.',
    'have to': 'I have to finish my assignment before tomorrow.',
    'headache': 'I have a terrible headache, so I need to take aspirin.',
    'helicopter': 'A helicopter flew low over the rescue area.',
    'here': 'Please wait here until your name is called.',
    'hey': 'Hey, what are you doing this weekend?',
    'historic': 'Borobudur is a historic temple built in the 9th century.',
    'historical': 'She enjoys reading historical novels set in medieval times.',
    'hockey': 'Field hockey is a fast and exciting team sport.',
    'holy': 'Jerusalem is considered a holy city by three major religions.',
    'homework': 'Don’t forget to complete your English homework tonight.',
    'honour': 'It was a great honour to receive the teacher award.',
    'horrible': 'The weather yesterday was horrible with heavy rain and wind.',
    'hunting': 'Hunting endangered animals is strictly illegal.',
    'hurricane': 'The strong hurricane damaged many houses near the coast.',
    'illustration': 'The children’s book features beautiful color illustrations.',
    'imaginary': 'Children often create imaginary friends when playing.',
    'imagination': 'Reading books sparks children’s creativity and imagination.',
    'immigrant': 'Many immigrants came to the country looking for new opportunities.',
    'impatient': 'The passengers grew impatient as the train was delayed.',
    'imply': 'Her tone seemed to imply that she was not satisfied.',
    'import': 'Indonesia imports wheat from Australia and Canada.',
    'impose': 'The government decided to impose stricter environmental regulations.',
    'included': 'Breakfast is included in the hotel room price.',
    'incredible': 'The view from the top of the mountain was incredible.',
    'incredibly': 'She solved the complicated puzzle incredibly fast.',
    'indoor': 'They have an indoor swimming pool for winter use.',
    'insight': 'The lecture provided valuable insights into modern economics.',
    'inspire': 'Her brave story inspired many young girls to study science.',
    'instructor': 'The driving instructor was patient and calm.',
    'intense': 'The athletes went through intense training before the Olympics.',
    'investigation': 'The police opened an investigation into the robbery.',
    'invitation': 'We received an invitation to their wedding ceremony.',
    'its': 'The cat licked its paws after eating.',
    'jazz': 'He loves playing saxophone in a jazz band.',
    'jewellery': 'She keeps her gold jewellery in a safe box.',
    'journal': 'She wrote about her daily thoughts in a personal journal.',
    'killing': 'The military action resulted in the killing of innocent civilians.',
    'kilometre': 'Our school is about three kilometres away from home.',
    'lab': 'Students conducted chemistry experiments in the science lab.',
    'labour': 'Manual labour can be physically demanding.',
    'laptop': 'He opened his laptop to attend the online meeting.',
    'laughter': 'Her room was always filled with joy and laughter.',
    'leadership': 'Good leadership inspires trust and teamwork.',
    'learning': 'Language learning requires patience and daily practice.',
    'leisure': 'In his leisure time, he enjoys gardening and reading.',
    'licence': 'You must pass the driving test to obtain a driver’s licence.',
    'lifestyle': 'Regular exercise and healthy eating are part of a good lifestyle.',
    'lion': 'The male lion has a thick and majestic mane.',
    'listener': 'A good teacher is always an attentive listener.',
    'lively': 'The market was lively and filled with colourful stalls.',
    'located': 'The hotel is conveniently located near the train station.',
    'long-term': 'Investing in education yields long-term benefits.',
    'lorry': 'A large lorry delivered the building materials to the site.',
    'luxury': 'Staying in a five-star hotel is a true luxury.',
    'maths': 'Our teacher explained the new maths formula clearly.',
    'metre': 'The swimming pool is fifty metres long.',
    'minority': 'Ethnic minority cultures should be protected and celebrated.',
    'modify': 'You can modify the document settings to suit your needs.',
    'monkey': 'The clever monkey peeled the fruit before eating it.',
    'motorcycle': 'Wearing a helmet is mandatory when riding a motorcycle.',
    'multiple': 'The exam consists of multiple choice questions.',
    'narrative': 'The novel tells a compelling narrative of survival and hope.',
    'native': 'She is a native speaker of Bahasa Indonesia.',
    'necessarily': 'Expensive items are not necessarily of better quality.',
    'neighbour': 'Our next-door neighbour is very kind and helpful.',
    'neighbourhood': 'We live in a quiet and friendly neighbourhood.',
    'nevertheless': 'It was raining heavily; nevertheless, we went for our walk.',
    'next to': 'The bookstore is located next to the bank.',
    'nightmare': 'He woke up sweating after having a bad nightmare.',
    'no one': 'No one answered the phone when I called.',
    'notion': 'She rejected the notion that girls cannot excel in engineering.',
    'obligation': 'Parents have a moral obligation to care for their children.',
    'ok': 'Everything is going to be OK, don’t worry.',
    'old-fashioned': 'My grandfather prefers writing letters with an old-fashioned pen.',
    'opening': 'The grand opening of the new shopping mall is this Saturday.',
    'opponent': 'He shook hands with his chess opponent before the game.',
    'opposed': 'Many local residents are opposed to building a new highway.',
    'organ': 'The heart is a vital organ in the human body.',
    'organizer': 'The event organizer did an excellent job with the arrangements.',
    'outcome': 'We are eagerly waiting for the outcome of the competition.',
    'oven': 'Bake the cake in a preheated oven for thirty minutes.',
    'pace': 'He walked at a steady pace along the quiet path.',
    'palace': 'The royal family lives in the historic palace.',
    'panel': 'Solar panels on the roof generate clean electricity.',
    'paragraph': 'Please write a short paragraph summarizing the story.',
    'parliament': 'The law was debated and passed by the national parliament.',
    'passport': 'Make sure your passport is valid before traveling abroad.',
    'penny': 'He saved every single penny to buy his first computer.',
    'pension': 'Retirees receive a monthly pension from the government.',
    'per cent': 'Over eighty per cent of the students passed the final exam.',
    'percentage': 'A large percentage of workers commute by train.',
    'perspective': 'Traveling gives you a broader perspective on life.',
    'pet': 'Having a pet dog teaches children responsibility.',
    'petrol': 'The price of petrol has increased this month.',
    'pleased': 'The teacher was very pleased with our test results.',
    'poet': 'Chairil Anwar is a legendary Indonesian poet.',
    'policeman': 'The policeman directed the traffic during the power outage.',
    'popularity': 'The popularity of online learning has grown rapidly.',
    'portrait': 'The museum features a famous portrait of the queen.',
    'pose': 'The family gathered in the garden to pose for a photo.',
    'poster': 'Students created educational posters about protecting the environment.',
    'poverty': 'Education is an effective tool to reduce global poverty.',
    'practise': 'You must practise speaking English every day to improve.',
    'praise': 'The teacher praised the students for their hard work.',
    'pray': 'Many people pray for peace and good health.',
    'prayer': 'They gathered in the mosque for Friday prayer.',
    'predict': 'Meteorologists predict heavy rainfall tomorrow morning.',
    'prediction': 'His prediction about the match result turned out to be correct.',
    'prepared': 'She was thoroughly prepared for the job interview.',
    'priest': 'The church priest conducted the Sunday service.',
    'prime': 'Tourism is the prime source of income for the island.',
    'prince': 'The young prince was admired for his humility.',
    'princess': 'The fairy tale tells the story of a brave princess.',
    'printing': 'Modern 3D printing technology is revolutionizing medicine.',
    'privacy': 'Everyone deserves privacy in their personal communications.',
    'prize': 'She won the first prize in the national speech contest.',
    'profile': 'You can update your personal profile on the school website.',
    'programme': 'The TV channel broadcasts educational programmes for kids.',
    'pronounce': 'Can you show me how to pronounce this difficult word?',
    'properly': 'Make sure you wear your seatbelt properly.',
    'psychologist': 'She consulted a child psychologist to help with her son.',
    'psychology': 'He is studying psychology at the university.',
    'pub': 'They met at a traditional English pub for a drink.',
    'pupil': 'The primary school has over five hundred pupils.',
    'purple': 'She wore a stylish purple jacket to the party.',
    'queue': 'There was a long queue outside the cinema.',
    'quotation': 'The article begins with an inspirational quotation by Einstein.',
    'racing': 'Horse racing is a traditional sport in many cultures.',
    'receipt': 'Always keep your store receipt in case you need a refund.',
    'reception': 'Please register at the front desk reception upon arrival.',
    'recommendation': 'The doctor gave her a recommendation for a balanced diet.',
    'recycle': 'Our community recycles plastic bottles, glass, and paper.',
    'red': 'The red roses in the garden blossomed beautifully.',
    'reliable': 'He is a reliable friend who always keeps his promises.',
    'reserve': 'You should reserve a table at the restaurant in advance.',
    'retired': 'My retired grandfather enjoys gardening every morning.',
    'revise': 'Students should revise their lecture notes before the exam.',
    'rid': 'We used natural repellent to get rid of mosquitoes.',
    'robot': 'The automated robot vacuum cleaned the living room floor.',
    'rubber': 'Indonesia is one of the world’s major producers of natural rubber.',
    'rugby': 'Rugby is an intense contact sport popular in New Zealand.',
    'sailor': 'The experienced sailor navigated the ship through the storm.',
    'salad': 'We had a healthy green salad with olive oil dressing.',
    'sandwich': 'I packed a cheese and tuna sandwich for lunch.',
    'satellite': 'Weather satellites track typhoons from outer space.',
    'saturday': 'We usually go grocery shopping on Saturday morning.',
    'scan': 'Please scan the QR code to view the restaurant menu.',
    'school': 'Children walk to the neighborhood school together.',
    'script': 'The director and actors reviewed the movie script.',
    'sculpture': 'The bronze sculpture was displayed in the town square.',
    'secondly': 'Secondly, we must ensure all safety protocols are followed.',
    'sequence': 'Follow the correct sequence of steps to assemble the table.',
    'series': 'I watched an exciting mystery series on Netflix.',
    'servant': 'In historical dramas, wealthy families often had servants.',
    'setting': 'The island was the perfect setting for the romantic film.',
    'seven': 'There are seven days in a week.',
    'seventeen': 'She celebrated her seventeenth birthday with close friends.',
    'seventy': 'My grandmother celebrated her seventieth anniversary.',
    'sheep': 'A flock of white sheep grazed on the green hillside.',
    'shy': 'He was shy at first, but soon made friends with his classmates.',
    'similarity': 'There is a strong similarity between the two sisters.',
    'singing': 'Her beautiful singing captivated the entire audience.',
    'ski': 'They went on a holiday to ski in the Swiss Alps.',
    'skiing': 'Skiing down the snowy mountain slope was thrilling.',
    'slave': 'The abolition of slave trade was a historic milestone.',
    'smartphone': 'Almost everyone uses a smartphone for daily tasks.',
    'smoking': 'Smoking cigarettes is strictly prohibited in hospital areas.',
    'soccer': 'Soccer is the most popular sport played worldwide.',
    'software': 'Our IT department installed the latest security software.',
    'solar': 'Solar energy is a clean and renewable source of power.',
    'solid': 'Ice is water in its solid state.',
    'specialist': 'She consulted a medical specialist for her back pain.',
    'specifically': 'The training program is designed specifically for beginners.',
    'spelling': 'Pay attention to English spelling when writing your essay.',
    'spending': 'The government increased spending on public healthcare.',
    'sponsor': 'A major tech company agreed to sponsor the school competition.',
    'stadium': 'The football stadium was packed with enthusiastic fans.',
    'stare': 'It is impolite to stare at people in public.',
    'statistic': 'Recent statistics show an increase in online shopping.',
    'sticky': 'Honey left a sticky mark on the kitchen counter.',
    'succeed': 'With dedication and hard work, you will surely succeed.',
    'summarize': 'Can you summarize the main points of the article?',
    'supermarket': 'We bought fresh fruit and milk at the supermarket.',
    'surgery': 'The patient underwent heart surgery and is recovering well.',
    'surprise': 'They planned a wonderful surprise birthday party for him.',
    'surprised': 'She was pleasantly surprised to receive a bouquet of flowers.',
    'surprising': 'It is not surprising that he won the championship.',
    'sweater': 'She knitted a warm wool sweater for winter.',
    'swimming': 'Swimming is a great exercise for strengthening the heart.',
    'symptom': 'Fever and coughing are common symptoms of the flu.',
    't-shirt': 'He wore a casual white t-shirt and blue jeans.',
    'tale': 'The grandmother told an enchanting fairy tale before bedtime.',
    'talented': 'She is a talented pianist who plays with great passion.',
    'tape': 'Use adhesive tape to seal the cardboard package.',
    'taxi': 'We hailed a taxi to take us to the airport.',
    'teenage': 'The magazine addresses issues facing teenage students.',
    'teenager': 'As a teenager, he enjoyed skateboarding and playing games.',
    'ten': 'Count from one to ten in English.',
    'tennis': 'They enjoy playing tennis on Sunday mornings.',
    'therapy': 'Physical therapy helped him walk again after the accident.',
    'tourism': 'Tourism provides vital economic support to the local community.',
    'tradition': 'Celebrating harvest festivals is an ancient local tradition.',
    'trainer': 'The personal trainer helped him design a fitness routine.',
    'transition': 'The school helped students make a smooth transition to college.',
    'truly': 'I am truly grateful for your help and support.',
    'update': 'Please update the app to get the newest features.',
    'venue': 'The hotel ballroom was chosen as the wedding venue.',
    'viewer': 'Millions of viewers watched the live broadcast of the World Cup.',
    'virtual': 'They attended a virtual conference through an online platform.',
    'visual': 'Visual aids like diagrams make learning much easier.',
    'vitamin': 'Oranges and lemons are rich in vitamin C.',
    'volunteer': 'She works as a volunteer at the local animal shelter.',
    'washing': 'She hung the clean washing on the clothesline.',
    'wealthy': 'The wealthy businessman donated millions to charity.',
    'wednesday': 'We have an English quiz every Wednesday morning.',
    'wildlife': 'The national park protects diverse wildlife and tropical plants.',
    'wind': 'A gentle cool wind blew across the beach.',
    'wire': 'Electricians replaced the damaged electrical wires.',
    'worldwide': 'English is widely spoken as a global language worldwide.',
    'wound': 'The nurse cleaned and bandaged the minor wound.',
    'wow': 'Wow, that was an absolutely incredible performance!'
}

from enrich_dataset import custom_id_trans, clean_sql_trans, get_arti

# Pronunciation function with eng_to_ipa
def get_pronunciation(word, base_clean):
    # Try base clean
    w = base_clean.lower().strip()
    # clean digits
    w = re.sub(r'\d+', '', w)
    w = re.sub(r'\(.*?\)', '', w).strip()
    if ',' in w:
        w = w.split(',')[0].strip()
    try:
        p = ipa.convert(w)
        # eng_to_ipa puts an asterisk * if unknown
        if '*' in p:
            p = p.replace('*', '')
        return f"/{p}/"
    except Exception:
        return f"/{w}/"

# Build full records
full_dataset = []
global_id = 1

for p in parsed:
    w = p['word'].strip()
    level = p['level']
    pos = p['pos']
    raw_entry = p['raw']
    
    # base clean for lookup
    b_clean = re.sub(r'\d+', '', w)
    b_clean = re.sub(r'\(.*?\)', '', b_clean).strip()
    if ',' in b_clean:
        b_clean = b_clean.split(',')[0].strip()
    
    # 1. Pronunciation
    pron = get_pronunciation(w, b_clean)
    
    # 2. Arti (Bahasa Indonesia)
    arti = get_arti(w, b_clean)
    
    # 3. Contoh Kalimat (English)
    b_low = b_clean.lower()
    if b_low in curated_sentences:
        example = curated_sentences[b_low]
    elif w.lower() in curated_sentences:
        example = curated_sentences[w.lower()]
    elif b_low in examples_map:
        example = examples_map[b_low]
    else:
        # Fallback
        example = f"Learning the word '{b_clean}' is essential for {level} level English."
        
    full_dataset.append({
        'no': global_id,
        'level': level,
        'word': w,
        'pronunciation': pron,
        'pos': pos,
        'arti': arti,
        'contoh_kalimat': example,
        'full_entry': raw_entry
    })
    global_id += 1

print(f"Total full dataset generated: {len(full_dataset)}")
print("Sample first 3:")
for item in full_dataset[:3]:
    print(item)
print("Sample last 3:")
for item in full_dataset[-3:]:
    print(item)

with open('oxford_3000_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(full_dataset, f, ensure_ascii=False, indent=2)

print("Saved to oxford_3000_enriched.json successfully!")
