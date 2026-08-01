from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_setup import get_engine,Earthquake


RESET = '\033[0m'
YELLOW = '\033[93m'

#determine largest frequency of depth
def most_replicated_depth(session):
    
    depth_frequency=(session.query(Earthquake.depth,func.count().label("count"))
                   .group_by(Earthquake.depth)
                    .all())
    depth_frequency_dict={depth:count for depth,count in depth_frequency}
    max_count=0
    for dep in depth_frequency_dict:
        if depth_frequency_dict.get(dep)>=max_count:
            max_count=depth_frequency_dict.get(dep)
            target_depth=dep
    print(f">>>> Earthquakes with Depth {target_depth} Have Maximum  Frequency {max_count} in the Database !")     



#determine largest frequency of magnitude
def most_replicated_magnitude(session):
    
    magnitude_frequency=(session.query(Earthquake.magnitude,func.count().label("count"))
                         .group_by(Earthquake.magnitude)
                         .all())
    magnitude_frequency_dict={magnitude:count for magnitude,count in magnitude_frequency}
    max_count=0
    for mag in magnitude_frequency_dict:
        if magnitude_frequency_dict.get(mag)>=max_count:
            max_count=magnitude_frequency_dict.get(mag)
            target_magnitude=mag
    print(f">>>> Earthquakes with Magnitude {target_magnitude} Have Maximum Frequency {max_count} in the Database !")   



#determine if all sources cover weak earthquakes
def analzye_weak_earthquake(session):
    
    #get list of different sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    #get sources cover weak earthquakes
    weak_count_query=(session.query(Earthquake.source,func.count().label("count")).
                      filter(Earthquake.magnitude<4)
                      .group_by(Earthquake.source)
                      .all())
    all_sources={source for (source,) in all_sources_query}
    weak_count={source:count for source,count in weak_count_query}

    #get sources  not cover weak earthquakes
    source_without_weak=[]
    for source in all_sources:
        if  source not in weak_count:
            source_without_weak.append(source)
    #print list of sources not cover weak earthquakes if exists
    if len(source_without_weak)!=0:
        print(">>>> All Sources Not Cover Weak Earthquakes")
        print(">>>> Sources With No Weak Earthquakes :")
        for s in source_without_weak:
            print(s)
    else:
        print(">>>> All Sources Cover Weak Earthquakes.")   



#Compare sources cover weak earthquakes through weak earthquakes percent
def compare_weak_sources(session):
   
    #get list of different sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    all_sources={source for (source,) in all_sources_query}
     #get total earthquake for each source
    total_earthquakes_query=(session.query(Earthquake.source,func.count().label("count"))
                                 .group_by(Earthquake.source)
                                 .all())
    total_earthquake_dict={source:count for source,count in total_earthquakes_query}
    for source in all_sources:
        #get  number of weak earthquakes registered for this source
        weak_earthquakes = (
            session.query(func.count())
            .filter(
                Earthquake.source == source,
                Earthquake.magnitude < 4
            )
            .scalar()
        )
    
        if total_earthquake_dict.get(source)==0:
            weak_percent=0
            print(f">>>> Weak Earthquake Percent for Source {source} is {weak_percent}% .")    
        else:
            weak_percent=weak_earthquakes/total_earthquake_dict.get(source)*100
            print(f">>>> Weak Earthquake Percent for Source {source} is {weak_percent:.2f}% .") 



#get average depth for strong earthquakes       
def analyze_strong_earthquake_depth(session):
    
    avg_depth_strong=(session.query(func.avg(Earthquake.depth)).
                          filter(Earthquake.magnitude>=6)
                           .scalar())
    if avg_depth_strong==None:
        print(">>>> Strong Earthquake Are Not Registered in Earthquak_db !")
    else:  
        print(f">>>> Strong Earthquake Usually Happens at an Average Depth of {avg_depth_strong} !")      


              
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
    print(f">>>> Number of Dangerous Earthquakes"
          f"High magnitude and Low Depth : {len(dangerous_earthquakes)}")

    for element in dangerous_earthquakes:
        print(f">>>> ID {element.id} ,Magnitude {element.magnitude}, Depth {element.depth} ")

#compare strong earthquakes,their magnitude >=6, in each sources        
def analyze_strong_earthquake_count(session):
    
    #get all sources
    all_sources_query=session.query(Earthquake.source).distinct().all()
    all_sources={source for (source,) in all_sources_query}
    #get total earthquake for each source
    total_earthquakes_query=(session.query(Earthquake.source,func.count().label("count"))
                             .group_by(Earthquake.source)
                             .all())
    total_earthquake_dict={source:count for source,count in total_earthquakes_query}
    #calculate number of strong earthquakes,their magnitude >=6.
    strong_earthquakes=(session.query(Earthquake.source,func.count().label("count"))
                       .filter(Earthquake.magnitude>=6)
                       .group_by(Earthquake.source)
                       .all())
    strong_earthquakes_dict={source:count for source,count in strong_earthquakes}

    #print result
    for source in all_sources:
        if source not in strong_earthquakes_dict:
            print(f">>>> {0} Strong Earthquakes Registered for Source {source}")
            print(f">>>> Strong Earthquake Percent for Source {source} is {0.0}%") 
        else:
            #get strong earthquake percent in each source
            strong_percent=strong_earthquakes_dict.get(source)/total_earthquake_dict.get(source)*100
            print(f">>>> Number of Strong Earthquakes Registered for Source {source} : {strong_earthquakes_dict.get(source)} ") 
            print(f">>>> Strong Earthquake Percent for Source {source} is {strong_percent:.2f}%") 

#analyze behaviour of earthquake in Japan during last month    
def analyze_japan_earthquake_behaviour(session):

    total_number=session.query(func.count(Earthquake)).scalar()

    #extract strong earthquake's data
    number_strong_earthquakes=(session.query(Earthquake.source,func.count().label("count"))
                             .filter(Earthquake.magnitude>=6)
                             .group_by(Earthquake.source)
                             .all())
    avg_strong_earthquakes=(session.query(func.avg(Earthquake.depth))
                            .filter(Earthquake.magnitude>=6)
                            .scalar())
    max_strong_earthquakes=(session.query(func.max(Earthquake.depth))
                            .filter(Earthquake.magnitude>=6)
                            .scalar())
    min_strong_earthquakes=(session.query(func.min(Earthquake.depth))
                            .filter(Earthquake.magnitude>=6)
                            .scalar())
    #extract moderate earthquake's data
    number_moderate_earthquakes=(session.query(Earthquake.source,func.count().label("count"))
                                .filter(Earthquake.magnitude<6 and Earthquake.magnitude>=4)
                                .group_by(Earthquake.source)
                                .all())
    avg_moderate_earthquakes=(session.query(func.avg(Earthquake.depth))
                              .filter(Earthquake.magnitude<6 and Earthquake.magnitude>=4)
                              .scalar())
    max_moderate_earthquakes=(session.query(func.max(Earthquake.depth))
                              .filter(Earthquake.magnitude<6 and Earthquake.magnitude>=4)
                              .scalar())
    min_moderate_earthquakes=(session.query(func.min(Earthquake.depth))
                              .filter(Earthquake.magnitude<6 and Earthquake.magnitude>=4)
                              .scalar())

    #extract weak earthquake's data
    number_weak_earthquakes=(session.query(Earthquake.source,func.count().label("count"))
                             .filter(Earthquake.magnitude<4)
                             .group_by(Earthquake.source).all())
    avg_weak_earthquakes=(session.query(func.avg(Earthquake.depth))
                          .filter(Earthquake.magnitude<4)
                          .scalar())
    max_weak_earthquakes=(session.query(func.max(Earthquake.depth))
                          .filter(Earthquake.magnitude<4)
                          .scalar())
    min_weak_earthquakes=(session.query(func.min(Earthquake.depth))
                          .filter(Earthquake.magnitude<4)
                          .scalar())
    
    print(f">>>> During Last Month {total_number} Earthquakes Registered in Japan ")
    print(">>>> Among them : ")
    print(f">>>> {number_weak_earthquakes} Weak Earthquakes with average depth {avg_weak_earthquakes}, maximum depth {max_weak_earthquakes} ,minimum depth {min_weak_earthquakes} ")
    print(f">>>> {number_moderate_earthquakes} Moderate Earthquakes with average depth {avg_moderate_earthquakes}, maximum depth {max_moderate_earthquakes} ,minimum depth {min_moderate_earthquakes} ")
    print(f">>>> {number_strong_earthquakes} Strong Earthquakes with average depth {avg_strong_earthquakes}, maximum depth {max_strong_earthquakes} ,minimum depth {min_strong_earthquakes} ")
    print("Are Registered .")

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

    print(">>>> You can Choose among Different Sources According blow Information and Your Priority  ")
    print(f">>>> Source {target_source} Register the Greatest Earthquake Counts {max_count} so It Offers More Precise Data")
    
    print(f">>>> Source {magnitude_source} Register the Greatest Average of Magnitude {max_magnitude_average} so It Prioritize Magnitude ")

    print(f">>>> Source {depth_source} Register the Greatest Average of depth {max_depth_average} so It Prioritize depth ")

def analyze_database():

    #connect to engine and make a session 
    engine,success=get_engine()
    if success:
       Session=sessionmaker(bind=engine)
       session=Session()
       print(f"{YELLOW}-------- Database Analyze --------{RESET}")
       print(f"{YELLOW}Q: What is Depth of the Most Frequent Earthquakes ?{RESET}\n")
       most_replicated_depth(session)
       print(f"{YELLOW}Q: What is Magnitude of the Most Frequent Earthquakes ?{RESET}\n")
       most_replicated_magnitude(session)
       print(f"{YELLOW}Q: Do All Sources Cover Weak Earthquakes ?{RESET}\n")
       analzye_weak_earthquake(session)
       print(f"{YELLOW}Q: What is the difference between Sourcse Cover Weak Earthquakes ?{RESET}\n")
       compare_weak_sources(session)
       print(f"{YELLOW}Q: Which Depth Do usually Strong Earthquakes Happen at ?{RESET}\n")
       analyze_strong_earthquake_depth(session)
       print(f"{YELLOW}Q: Sort Dangerous Earthquakes. {RESET}\n")
       analyze_dangerous_earthquake_order(session)
       print(f"{YELLOW}Q: Compare Strong Earthquakes for Each Source. {RESET}\n")
       analyze_strong_earthquake_count(session)
       print(f"{YELLOW}Q: What is the Scientific Conclusion of JAPAN's Earthquake Behaviour ? {RESET}\n")
       analyze_japan_earthquake_behaviour(session)
       print(f"{YELLOW}Q: What is Your Suggestion for Combination of Sources ? {RESET}\n")
       analyze_source_combination_suggestion(session)
    