from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from src.database_setup import get_engine,Earthquake

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
BOLD = '\033[1m'
RESET = '\033[0m'

#determine largest frequency of depth
def most_replicated_depth(session):
    
    depth_frequency=(session.query(Earthquake.depth,func.count().label("count")).group_by(Earthquake.depth).all())
    depth_frequency_dict={depth:count for depth,count in depth_frequency}
    max_count=0
    for dep in depth_frequency_dict:
        if depth_frequency_dict.get(dep)>=max_count:
            max_count=depth_frequency_dict.get(dep)
            target_depth=dep
    print(f"{BOLD}>>>> Earthquakes with Depth {BLUE}{target_depth}{RESET}{BOLD} Have Maximum  Frequency {BLUE} {max_count} {RESET}{BOLD}in the Database !{RESET}")     



#determine largest frequency of magnitude
def most_replicated_magnitude(session):
    
    magnitude_frequency=(session.query(Earthquake.magnitude,func.count().label("count")).group_by(Earthquake.magnitude).all())
    magnitude_frequency_dict={magnitude:count for magnitude,count in magnitude_frequency}
    max_count=0
    for mag in magnitude_frequency_dict:
        if magnitude_frequency_dict.get(mag)>=max_count:
            max_count=magnitude_frequency_dict.get(mag)
            target_magnitude=mag      
    print(f"{BOLD}>>>> Earthquakes with Magnitude {BLUE} {target_magnitude}{RESET}{BOLD} Have Maximum Frequency{BLUE} {max_count}{RESET}{BOLD} in the Database !{RESET}")   



#determine if all sources cover weak earthquakes
def analzye_weak_earthquake(session):
    
    #get list of different sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    #get sources cover weak earthquakes
    weak_count_query=(session.query(Earthquake.source,func.count().label("count")).filter(Earthquake.magnitude<4.0).group_by(Earthquake.source).all())
    all_sources={source for (source,) in all_sources_query}
    weak_count={source:count for source,count in weak_count_query}

    #get sources  not cover weak earthquakes
    source_without_weak=[]
    for source in all_sources:
        if  source not in weak_count:
            source_without_weak.append(source)
    #print list of sources not cover weak earthquakes if exists
    if len(source_without_weak)!=0:
        print(f"{BOLD}>>>> All Sources Not Cover Weak Earthquakes{RESET}")
        print(f"{BOLD}>>>> Sources With No Weak Earthquakes :{RESET}")
        for s in source_without_weak:
            print(f"{BOLD}{GREEN}{s}{RESET}")
    else:
        print(f"{BOLD}>>>> All Sources Cover Weak Earthquakes.{RESET}")   



#Compare sources cover weak earthquakes through weak earthquakes percent
def compare_weak_sources(session):
   
    #get list of different sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    all_sources={source for (source,) in all_sources_query}
    #get total earthquake for each source
    total_earthquakes_query=(session.query(Earthquake.source,func.count().label("count")).group_by(Earthquake.source).all())
    total_earthquake_dict={source:count for source,count in total_earthquakes_query}
    for source in all_sources:
        #get  number of weak earthquakes registered for this source
        weak_earthquakes = (
            session.query(func.count())
            .filter(
                Earthquake.source == source,
                Earthquake.magnitude < 4.0
            )
            .scalar()
        )
    
        if total_earthquake_dict.get(source)==0:
            weak_percent=0
            print(f"{BOLD}>>>> Weak Earthquake Percent for Source {BLUE}{source} {RESET}{BOLD} is {BLUE}{weak_percent}% {RESET}")    
        else:
            weak_percent=weak_earthquakes/total_earthquake_dict.get(source)*100
            print(f"{BOLD}>>>> Weak Earthquake Percent for Source {BLUE} {source}{RESET}{BOLD} is{BLUE} {weak_percent:.2f}% {RESET}") 



#get average depth for strong earthquakes       
def analyze_strong_earthquake_depth(session):
    
    avg_depth_strong=(session.query(func.avg(Earthquake.depth)).
                          filter(Earthquake.magnitude>=6.0)
                           .scalar())
    if avg_depth_strong==None:
        print(f"{BOLD}>>>> Strong Earthquake Are Not Registered in Earthquak_db !{RESET}")
    else:  
        print(f"{BOLD}>>>> Strong Earthquake Usually Happens at an Average Depth of {RED} {avg_depth_strong} {RESET}!")      


              
#sort dangerous earthquake those have high magnitude and low depth  
def analyze_dangerous_earthquake_order(session):

    #first fetch earthquake have high magnitude and low depth
    #then order first by magnitude(descending) 
    #then order by depth (ascending)
    dangerous_earthquakes=(session.query(Earthquake).
                                filter(Earthquake.magnitude>=6 ,Earthquake.depth<10)
                                .order_by(Earthquake.magnitude.desc(),
                                          Earthquake.depth.asc())
                                          .all())

    print(f"{BOLD}>>>> Number of Dangerous Earthquakes"
          f"High magnitude and Low Depth :{RED} {len(dangerous_earthquakes)}{RESET}")
    for element in dangerous_earthquakes:
        print(f"{BOLD}>>>> ID {RED} {element.id}{RESET}{BOLD} ,Magnitude {RED} {element.magnitude}{RESET},{BOLD} Depth{RED} {element.depth}{RESET} ")

#compare strong earthquakes,their magnitude >=6, in each sources        
def analyze_strong_earthquake_count(session):
    
    #get all sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    all_sources={source for (source,) in all_sources_query}
    #get total earthquake for each source
    total_earthquakes_query=(session.query(Earthquake.source,func.count().label("count")).group_by(Earthquake.source).all())
    total_earthquake_dict={source:count for source,count in total_earthquakes_query}
    #calculate number of strong earthquakes,their magnitude >=6.
    strong_earthquakes=(session.query(Earthquake.source,func.count().label("count")).filter(Earthquake.magnitude>=6).group_by(Earthquake.source).all())
    strong_earthquakes_dict={source:count for source,count in strong_earthquakes}

    #print result
    for source in all_sources:
        if source not in strong_earthquakes_dict:
            print(f"{BOLD}>>>> {BLUE}{0} {RESET}{BOLD}Strong Earthquakes Registered for Source {BLUE}{source}{RESET}")
            print(f"{BOLD}>>>> Strong Earthquake Percent for Source{BLUE} {source}{RESET}{BOLD} is {BLUE}{0.0}%{RESET}") 
        else:
            #get strong earthquake percent in each source
            strong_percent=strong_earthquakes_dict.get(source)/total_earthquake_dict.get(source)*100
            print(f"{BOLD}>>>> Number of Strong Earthquakes Registered for Source{BLUE} {source} {RESET}:{BOLD}{BLUE} {strong_earthquakes_dict.get(source)}{RESET} ") 
            print(f"{BOLD}>>>> Strong Earthquake Percent for Source {BLUE} {source} {RESET} is {BOLD}{BLUE}  {strong_percent:.2f}% {RESET}") 

#analyze behaviour of earthquake in Japan during last month    
def analyze_japan_earthquake_behaviour(session):

    total_number=session.query(func.count(Earthquake.id)).scalar()

    #extract strong earthquake's data
    number_strong_earthquakes=(session.query(func.count(Earthquake.id)).filter(Earthquake.magnitude>=6.0).scalar())
    avg_strong_earthquakes=(session.query(func.avg(Earthquake.depth)).filter(Earthquake.magnitude>=6.0).scalar())
    max_strong_earthquakes=(session.query(func.max(Earthquake.depth)).filter(Earthquake.magnitude>=6.0).scalar())
    min_strong_earthquakes=(session.query(func.min(Earthquake.depth)).filter(Earthquake.magnitude>=6.0).scalar())
    #extract moderate earthquake's data
    number_moderate_earthquakes=(session.query(func.count(Earthquake.id)).filter(Earthquake.magnitude<6.0 , Earthquake.magnitude>=4.0).scalar())
    avg_moderate_earthquakes=(session.query(func.avg(Earthquake.depth)).filter(Earthquake.magnitude<6.0 , Earthquake.magnitude>=4.0).scalar())
    max_moderate_earthquakes=(session.query(func.max(Earthquake.depth)).filter(Earthquake.magnitude<6.0 , Earthquake.magnitude>=4.0).scalar())
    min_moderate_earthquakes=(session.query(func.min(Earthquake.depth)).filter(Earthquake.magnitude<6.0 , Earthquake.magnitude>=4.0).scalar())

    #extract weak earthquake's data
    number_weak_earthquakes=(session.query(func.count(Earthquake.id)).filter(Earthquake.magnitude<4.0).scalar())
    avg_weak_earthquakes=(session.query(func.avg(Earthquake.depth)).filter(Earthquake.magnitude<4.0).scalar())
    max_weak_earthquakes=(session.query(func.max(Earthquake.depth)).filter(Earthquake.magnitude<4.0).scalar())
    min_weak_earthquakes=(session.query(func.min(Earthquake.depth)).filter(Earthquake.magnitude<4.0).scalar())
    
    print(f"{BOLD}>>>> During Last Month {BLUE}{total_number}{RESET}{BOLD} Earthquakes Registered in Japan {RESET}")
    print(f"{BOLD}>>>> Among them : ")
    print(f">>>>{BLUE} {number_weak_earthquakes}{RESET}{BOLD} Weak Earthquakes with average depth {BLUE} {avg_weak_earthquakes:.2f}{RESET}{BOLD}, maximum depth{BLUE} {max_weak_earthquakes}{RESET}{BOLD} ,minimum depth {BLUE}{min_weak_earthquakes}{RESET} ")
    print(f">>>>{BOLD}{BLUE} {number_moderate_earthquakes} {RESET}{BOLD}Moderate Earthquakes with average depth {BLUE}{avg_moderate_earthquakes:.2f}{RESET}{BOLD}, maximum depth{BLUE} {max_moderate_earthquakes}{RESET}{BOLD} ,minimum depth{BLUE} {min_moderate_earthquakes}{RESET} ")
    print(f">>>> {BOLD}{BLUE} {number_strong_earthquakes}{RESET}{BOLD} Strong Earthquakes with average depth{BLUE} {avg_strong_earthquakes:.2f}{RESET}{BOLD}, maximum depth {BLUE}{max_strong_earthquakes}{RESET}{BOLD} ,minimum depth {BLUE}{min_strong_earthquakes}{RESET} ")
    print(f"{BOLD}Are Registered .{RESET}")

#give a suggestion for source combination
def analyze_source_combination_suggestion(session):

    #get number of earthquakes register per source
    earthquake_frequency_query=(session.query(Earthquake.source,func.count().label("count"))
                                .group_by(Earthquake.source)
                                .all())
    earthquake_frequency={source:count for source,count in earthquake_frequency_query}
    max_count=0
    for source in earthquake_frequency:
        if earthquake_frequency.get(source)>max_count:
           max_count=earthquake_frequency.get(source)
           target_source=source

    #get avg of magnitude per source
    magnitude_avg_query=(session.query(Earthquake.source,func.avg(Earthquake.magnitude).label("average"))
                                .group_by(Earthquake.source)
                                .all())
    magnitude_average={source:average for source,average in magnitude_avg_query}
    max_magnitude_average=0
    for source in magnitude_average:
        if  magnitude_average.get(source)>max_magnitude_average:
            max_magnitude_average=magnitude_average.get(source)
            magnitude_source=source        

    
    #get avg of depth per source
    depth_avg_query=(session.query(Earthquake.source,func.avg(Earthquake.depth).label("average"))
                                .group_by(Earthquake.source)
                                .all())
    depth_average={source:average for source,average in depth_avg_query}
    max_depth_average=0
    for source in depth_average:
        if  depth_average.get(source)> max_depth_average:
            max_depth_average=depth_average.get(source)
            depth_source=source        

    print(f"{BOLD}>>>> You can Choose among Different Sources According Extracted Information and Your Priority {RESET} ")
    print(f"{BOLD}>>>> Source{BLUE} {target_source}{RESET}{BOLD} Register the Greatest Earthquake Counts{BLUE} {max_count}{RESET}{BOLD} So It Offers More Precise Data{RESET}")
    
    print(f"{BOLD}>>>> Source {BLUE} {magnitude_source}{RESET}{BOLD} Register the Greatest Average of Magnitude{BLUE} {max_magnitude_average:.2f}{RESET}{BOLD} So It Prioritize Magnitude{RESET} ")

    print(f"{BOLD}>>>> Source{BLUE} {depth_source}{RESET}{BOLD} Register the Greatest Average of depth {BLUE}{max_depth_average:.2f}{RESET}{BOLD} So It Prioritize depth {RESET}")

def analyze_database():

    #connect to engine and make a session 
    engine,success=get_engine()
    if success:
       Session=sessionmaker(bind=engine)
       session=Session()
       print(f"{YELLOW}-------- Database Analyze --------{RESET}")
       print("\n")
       print(f"{YELLOW}Q: What is Depth of the Most Frequent Earthquakes ?{RESET}\n")
       most_replicated_depth(session)
       print("\n")
       print(f"{YELLOW}Q: What is Magnitude of the Most Frequent Earthquakes ?{RESET}\n")
       most_replicated_magnitude(session)
       print("\n")
       print(f"{YELLOW}Q: Do All Sources Cover Weak Earthquakes ?{RESET}\n")
       analzye_weak_earthquake(session)
       print("\n")
       print(f"{YELLOW}Q: What is the difference between Sourcse Cover Weak Earthquakes ?{RESET}\n")
       compare_weak_sources(session)
       print("\n")
       print(f"{YELLOW}Q: Which Depth Do usually Strong Earthquakes Happen at ?{RESET}\n")
       analyze_strong_earthquake_depth(session)
       print("\n")
       print(f"{YELLOW}Q: Sort Dangerous Earthquakes. {RESET}\n")
       analyze_dangerous_earthquake_order(session)
       print("\n")
       print(f"{YELLOW}Q: Compare Strong Earthquakes for Each Source. {RESET}\n")
       analyze_strong_earthquake_count(session)
       print("\n")
       print(f"{YELLOW}Q: What is the Scientific Conclusion of JAPAN's Earthquake Behaviour ? {RESET}\n")
       analyze_japan_earthquake_behaviour(session)
       print("\n")
       print(f"{YELLOW}Q: What is Your Suggestion for Combination of Sources ? {RESET}\n")
       analyze_source_combination_suggestion(session)
    