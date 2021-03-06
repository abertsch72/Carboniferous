from nearby_cities import nearby_airports
from total_ground_cost import total_ground_cost
from total_air_cost import total_air_cost
from trip import Trip, TripStep
from copy import deepcopy


source_airport_code = ""
destination_airport_code = ""


"""
Parameters:
source: The name of the city to start from
destination: The name of the destination city
car_mpg: The number of miles per gallon that the user's car achieves
max_cost: The maximum cost in USD the user wishes to spend
max_time: The maximum number of houes the user wishes to spend travelling
depart_time: The date the user wishes to travel on. Format: YYYY-MM-DD
user_prefs: A 4 element array of booleans for whether the user wishes to travel
    with the given mode. [car, bus, train, plane]
key_vault: The vault that stores all of the API keys for the program
"""
def find_carbon_paths(source, destination, car_mpg, max_cost, max_time, depart_time, user_prefs, key_vault):
    trips = start_ground_trips(source, destination, car_mpg, user_prefs, key_vault)
    updated_trips = find_flights(trips, destination, max_cost, max_time, depart_time, user_prefs, key_vault)
    finished_trips = finish_trips(updated_trips, destination, max_cost, max_time, car_mpg, user_prefs, key_vault)
    finished_trips += direct_trips(source, destination, car_mpg, max_cost, max_time, depart_time, user_prefs, key_vault)
    top_five_trips = sort_by_carbon(finished_trips)
    return top_five_trips

"""

"""

def direct_trips(source, destination, car_mpg, max_cost, max_time, depart_time, user_prefs, key_vault):
    global source_airport_code
    global destination_airport_code
    return_list = []
    if user_prefs[0] or user_prefs[1] or user_prefs[2] == True:
        ground_cost = total_ground_cost(source,destination,car_mpg,key_vault)
        if user_prefs[0] and ground_cost[0][0] > 0:
            car_trip = Trip(source)
            car_trip_step = TripStep(destination,TripStep.CAR,ground_cost[0][0],ground_cost[0][1],ground_cost[0][2])
            car_trip.cities.append(car_trip_step)
            car_trip.carbon_cost += ground_cost[0][0]
            car_trip.money_cost += ground_cost[0][1]
            car_trip.time_cost += ground_cost[0][2]
            return_list.append(car_trip)
        if user_prefs[1] and ground_cost[1][0] > 0:
            bus_trip = Trip(source)
            bus_trip_step = TripStep(destination,TripStep.BUS,ground_cost[1][0],ground_cost[1][1],ground_cost[1][2])
            bus_trip.cities.append(bus_trip_step)
            bus_trip.carbon_cost += ground_cost[1][0]
            bus_trip.money_cost += ground_cost[1][1]
            bus_trip.time_cost += ground_cost[1][2]
            return_list.append(bus_trip)
        if user_prefs[2] and ground_cost[2][0] > 0:
            train_trip = Trip(source)
            train_trip_step = TripStep(destination,TripStep.TRAIN,ground_cost[2][0],ground_cost[2][1],ground_cost[2][2])
            train_trip.cities.append(train_trip_step)
            train_trip.carbon_cost += ground_cost[2][0]
            train_trip.money_cost += ground_cost[2][1]
            train_trip.time_cost += ground_cost[2][2]
            return_list.append(train_trip)
    if user_prefs[3]:
        plane_trip = Trip(source)
        plane_cost = total_air_cost(source_airport_code,destination_airport_code,depart_time)
        if plane_cost[0] > 0:
            plane_trip_step = TripStep(destination,TripStep.PLANE,plane_cost[0],plane_cost[1],plane_cost[2])
            plane_trip.cities.append(plane_trip_step)
            plane_trip.carbon_cost += plane_cost[0]
            plane_trip.money_cost += plane_cost[1]
            plane_trip.time_cost += plane_cost[2]
            return_list.append(plane_trip)
    return return_list


def sort_by_carbon(finished_trips):
    carbon_dictionary = {}
    for trip in finished_trips:
        carbon_dictionary[trip.carbon_cost] = trip

    top_five_carbons = list(carbon_dictionary.keys())
    top_five_carbons.sort()
    top_five_trips = []
    for val in top_five_carbons[:5]:
        top_five_trips.append(carbon_dictionary[val])
    return top_five_trips

"""
user_prefs: A 4 element array of booleans for whether the user wishes to travel
    with the given mode. [car, bus, train, plane]
"""
def start_ground_trips(source, destination, car_mpg, user_prefs, key_vault):
    global source_airport_code
    src_airports = nearby_airports(source, key_vault)
    source_airport_code = src_airports[0][1]
    trips = []
    for airport, code in src_airports:
        ground_paths = total_ground_cost(source, airport, car_mpg, key_vault)
        if user_prefs[0]:
            car_trip = Trip(source)
            car_costs = ground_paths[0]
            car_trip.carbon_cost += float(car_costs[0])
            car_trip.money_cost += car_costs[1]
            car_trip.time_cost += car_costs[2]
            car_trip.cities.append(TripStep(airport, TripStep.CAR, car_costs[0], car_costs[1], car_costs[2]))
            car_trip.prev_airport_code = code
            if car_trip.carbon_cost >= 0:
                trips.append(car_trip)
        if user_prefs[1]:
            bus_trip = Trip(source)
            bus_costs = ground_paths[1]
            bus_trip.carbon_cost += float(bus_costs[0])
            bus_trip.money_cost += bus_costs[1]
            bus_trip.time_cost += bus_costs[2]
            bus_trip.cities.append(TripStep(airport, TripStep.BUS, bus_costs[0], bus_costs[1], bus_costs[2]))
            bus_trip.prev_airport_code = code
            if bus_trip.carbon_cost >= 0:
                trips.append(bus_trip)

        if user_prefs[2]:
            train_trip = Trip(source)
            train_costs = ground_paths[2]
            train_trip.carbon_cost += float(train_costs[0])
            train_trip.money_cost += train_costs[1]
            train_trip.time_cost += train_costs[2]
            train_trip.cities.append(TripStep(airport, TripStep.TRAIN, train_costs[0], train_costs[1], train_costs[2]))
            train_trip.prev_airport_code = code
            if train_trip.carbon_cost >= 0:
                trips.append(train_trip)

    return trips

def find_flights(curr_trips, destination, max_cost, max_time, depart_time, user_prefs, key_vault):
    global destination_airport_code
    if not user_prefs[3]:
        return curr_trips

    end_cities = nearby_airports(destination, key_vault)
    destination_airport_code = end_cities[0][1]
    updated_trips = []
    for trip in curr_trips:
        if trip.money_cost >= max_cost or trip.time_cost >= max_time or trip.carbon_cost < 0:
            continue
        prev_code = trip.prev_airport_code
        if trip.get_last_city() != destination:
            for city in end_cities:
                airport_code = city[1]
                flight_cost = total_air_cost(prev_code, airport_code, depart_time)
                if flight_cost[0] >= 0:
                    curr_trip = deepcopy(trip)
                    flight_step = TripStep(city[1], TripStep.PLANE, flight_cost[0], flight_cost[1], flight_cost[2])
                    curr_trip.carbon_cost += flight_cost[0]
                    curr_trip.money_cost += flight_cost[1]
                    curr_trip.time_cost += flight_cost[2]
                    curr_trip.cities.append(flight_step)
                    updated_trips.append(curr_trip)
    return updated_trips

def finish_trips(curr_trips, destination, max_cost, max_time, car_mpg, user_prefs, key_vault):
    finished_trips = []
    for trip in curr_trips:
        prev_city = trip.get_last_city()
        if prev_city == destination:
            finished_trips.append(trip)
            continue
        ground_paths = total_ground_cost(prev_city, destination, car_mpg, key_vault)
        # By car
        if user_prefs[0] and ground_paths[0][0] > 0:
            car_costs = ground_paths[0]
            car_trip = deepcopy(trip)
            car_trip_step = TripStep(destination, TripStep.CAR, car_costs[0], car_costs[1], car_costs[2])
            car_trip.cities.append(car_trip_step)
            car_trip.carbon_cost += float(car_costs[0])
            car_trip.money_cost += car_costs[1]
            car_trip.time_cost += car_costs[2]
            if car_trip.money_cost <= max_cost and car_trip.time_cost <= max_time:
                finished_trips.append(car_trip)

        # By bus
        if user_prefs[1] and ground_paths[1][0] > 0:
            bus_costs = ground_paths[1]
            bus_trip = deepcopy(trip)
            bus_trip_step = TripStep(destination, TripStep.BUS, bus_costs[0], bus_costs[1], bus_costs[2])
            bus_trip.cities.append(bus_trip_step)
            bus_trip.carbon_cost += float(bus_costs[0])
            bus_trip.money_cost += bus_costs[1]
            bus_trip.time_cost += bus_costs[2]
            if bus_trip.money_cost <= max_cost and bus_trip.time_cost <= max_time:
                finished_trips.append(bus_trip)

        # By train
        if user_prefs[2]  and ground_paths[2][0] > 0:
            train_costs = ground_paths[2]
            train_trip = deepcopy(trip)
            train_trip_step = TripStep(destination, TripStep.TRAIN, train_costs[0], train_costs[1], train_costs[2])
            train_trip.cities.append(train_trip_step)
            train_trip.carbon_cost += float(train_costs[0])
            train_trip.money_cost += train_costs[1]
            train_trip.time_cost += train_costs[2]
            if train_trip.money_cost <= max_cost and train_trip.time_cost <= max_time:
                finished_trips.append(train_trip)

    return finished_trips

#from api_management import APIKeys
#print(find_carbon_paths("Tucson", "Seattle", 30, 1500, 12, "2020-01-25", [True, True, True, True], APIKeys()))
