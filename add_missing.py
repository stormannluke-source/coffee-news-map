#!/usr/bin/env python3
"""Add all missing businesses found during research to the CSV files."""

import csv, re

# Each entry: (name, address, city, state, zip, phone, email, website, category, town, suitable)
# suitable: 'Yes' or 'No'

MISSING = {
    'presque_isle_area': [
        # Presque Isle
        ("Marden's Surplus & Salvage", "803 Main St", "Presque Isle", "ME", "04769", "(207) 762-3417", "", "", "Discount Store", "Presque Isle", "Yes"),
        ("Eagle Hill Stamps & Coins", "351 Main St", "Presque Isle", "ME", "04769", "(207) 764-5701", "", "", "Collectibles", "Presque Isle", "Yes"),
        ("Wilder's Jewelry Store", "407 Main St", "Presque Isle", "ME", "04769", "(207) 764-0309", "", "", "Jewelry Store", "Presque Isle", "Yes"),
        ("The Sled Shop Inc.", "108 Main St", "Presque Isle", "ME", "04769", "(207) 764-2900", "", "", "Powersports Dealer", "Presque Isle", "Yes"),
        # Churches - Presque Isle
        ("Grant Memorial United Methodist Church", "79 Fleetwood St", "Presque Isle", "ME", "04769", "(207) 762-9351", "", "", "Religion", "Presque Isle", "No"),
        ("Presque Isle Congregational Church (UCC)", "27 Church St", "Presque Isle", "ME", "04769", "(207) 764-4743", "", "", "Religion", "Presque Isle", "No"),
        ("Presque Isle Seventh-day Adventist Church", "56 Park St", "Presque Isle", "ME", "04769", "(207) 768-6251", "", "", "Religion", "Presque Isle", "No"),
        ("Presque Isle Wesleyan Church", "387 Centerline Rd", "Presque Isle", "ME", "04769", "(207) 764-5187", "", "", "Religion", "Presque Isle", "No"),
        ("St. John's Episcopal Church", "52 2nd St", "Presque Isle", "ME", "04769", "(207) 764-4298", "", "", "Religion", "Presque Isle", "No"),
        ("St. Mary's Catholic Church (Nativity of the BVM)", "6 Roberts St", "Presque Isle", "ME", "04769", "(207) 768-3671", "", "", "Religion", "Presque Isle", "No"),
        ("Bethany Baptist Church", "24 2nd St", "Presque Isle", "ME", "04769", "(207) 768-8811", "", "", "Religion", "Presque Isle", "No"),
        ("Christ Gospel Church", "49 Church St", "Presque Isle", "ME", "04769", "(207) 764-4586", "", "", "Religion", "Presque Isle", "No"),
        ("Christian Life Assembly", "40 Chandler Rd", "Presque Isle", "ME", "04769", "(207) 764-1352", "", "", "Religion", "Presque Isle", "No"),
        ("New Life Baptist Church", "229 Caribou Rd", "Presque Isle", "ME", "04769", "(207) 764-0500", "", "", "Religion", "Presque Isle", "No"),
        ("State Street Baptist Church", "225 State St", "Presque Isle", "ME", "04769", "(207) 768-3041", "", "", "Religion", "Presque Isle", "No"),
        ("Family Worship Center", "265 Caribou Rd", "Presque Isle", "ME", "04769", "(207) 540-1060", "", "", "Religion", "Presque Isle", "No"),
        ("Beacon of Hope Ministries", "830 Main St", "Presque Isle", "ME", "04769", "(207) 768-7771", "", "", "Religion", "Presque Isle", "No"),
        ("First United Pentecostal Church", "53 Wilson St", "Presque Isle", "ME", "04769", "(207) 762-5581", "", "", "Religion", "Presque Isle", "No"),
        ("Full Gospel Assembly", "7 Dudley St", "Presque Isle", "ME", "04769", "(207) 764-4207", "", "", "Religion", "Presque Isle", "No"),
        ("Church of Jesus", "153 Chapman Rd", "Presque Isle", "ME", "04769", "(207) 764-4186", "", "", "Religion", "Presque Isle", "No"),
        ("Freedom Church", "830 Main St", "Presque Isle", "ME", "04769", "(207) 760-7491", "", "", "Religion", "Presque Isle", "No"),
        # Churches - Fort Fairfield
        ("St. Denis Catholic Church", "147 Main St", "Fort Fairfield", "ME", "04742", "(207) 498-2536", "", "", "Religion", "Fort Fairfield", "No"),
        ("St. Paul's Episcopal Church", "170 Main St", "Fort Fairfield", "ME", "04742", "(207) 492-4211", "", "", "Religion", "Fort Fairfield", "No"),
        ("United Parish Church (UCC/UMC)", "4 Church St", "Fort Fairfield", "ME", "04742", "", "", "", "Religion", "Fort Fairfield", "No"),
        ("Community Wesleyan Church", "9 Wesleyan St", "Fort Fairfield", "ME", "04742", "", "", "", "Religion", "Fort Fairfield", "No"),
        ("Celebration Center (Assemblies of God)", "170 Houlton Rd", "Fort Fairfield", "ME", "04742", "", "", "", "Religion", "Fort Fairfield", "No"),
        ("United Pentecostal Church", "33 Currier Rd", "Fort Fairfield", "ME", "04742", "", "", "", "Religion", "Fort Fairfield", "No"),
        ("Bethel Baptist Church", "1 Presque Isle St", "Fort Fairfield", "ME", "04742", "(207) 473-7772", "", "", "Religion", "Fort Fairfield", "No"),
        # Churches - Mars Hill
        ("St. Joseph Catholic Church", "17 Main St", "Mars Hill", "ME", "04758", "(207) 768-3671", "", "", "Religion", "Mars Hill", "No"),
        ("Mars Hill United Methodist Church", "20 Main St", "Mars Hill", "ME", "04758", "(207) 429-8022", "", "", "Religion", "Mars Hill", "No"),
        ("United Baptist Church", "20 Church St", "Mars Hill", "ME", "04758", "(207) 429-9590", "", "", "Religion", "Mars Hill", "No"),
        ("Full Gospel Assembly", "9 Maple St", "Mars Hill", "ME", "04758", "", "", "", "Religion", "Mars Hill", "No"),
        ("Apostolic Pentecostal Church", "88 Fort Rd", "Mars Hill", "ME", "04758", "", "", "", "Religion", "Mars Hill", "No"),
        # Churches - Mapleton
        ("Mapleton United Methodist Church", "Main St", "Mapleton", "ME", "04757", "(207) 764-4241", "", "", "Religion", "Mapleton", "No"),
        ("State Road Advent Christian Church", "1135 State Rd", "Mapleton", "ME", "04757", "(207) 764-1510", "", "", "Religion", "Mapleton", "No"),
        ("West Chapman Advent Christian Church", "W Chapman Rd", "Mapleton", "ME", "04757", "", "", "", "Religion", "Mapleton", "No"),
        # Churches - Washburn
        ("First Baptist Church of Washburn", "1268 Main St", "Washburn", "ME", "04786", "(207) 455-4839", "", "", "Religion", "Washburn", "No"),
        ("Lidstone Memorial United Methodist Church", "25 Hines St", "Washburn", "ME", "04786", "(207) 455-4726", "", "", "Religion", "Washburn", "No"),
        ("St. Catherine Catholic Church", "13 McManus St", "Washburn", "ME", "04786", "(207) 435-3591", "", "", "Religion", "Washburn", "No"),
        ("Washburn Pentecostal Church", "1202 Main St", "Washburn", "ME", "04786", "", "", "", "Religion", "Washburn", "No"),
        # Churches - Ashland
        ("Ashland Advent Christian Church", "42 Exchange St", "Ashland", "ME", "04732", "(207) 435-6669", "", "", "Religion", "Ashland", "No"),
        ("Ashland Union Congregational Church (UCC)", "48 Sheridan Rd", "Ashland", "ME", "04732", "(207) 435-6752", "", "", "Religion", "Ashland", "No"),
        ("St. Mark Catholic Church", "Allen Farm Rd", "Ashland", "ME", "04732", "", "", "", "Religion", "Ashland", "No"),
        ("Apostolic Church in Jesus Name", "697 Masardis Rd", "Ashland", "ME", "04732", "", "", "", "Religion", "Ashland", "No"),
        # Non-church religious buildings - Presque Isle
        ("Maine Hope Center (The Hope Chest)", "445 Main St", "Presque Isle", "ME", "04769", "(207) 764-1816", "", "", "Religion", "Presque Isle", "Yes"),
        ("Threads of Hope Thrift Store (Catholic Charities)", "830 Main St", "Presque Isle", "ME", "04769", "(207) 493-8919", "", "", "Religion", "Presque Isle", "Yes"),
        ("Crown of Maine Motors", "86 Parsons St", "Presque Isle", "ME", "04769", "(207) 768-0741", "", "", "Auto Sales", "Presque Isle", "Yes"),
        ("The Total Look", "40 North St Ste 5", "Presque Isle", "ME", "04769", "(207) 764-8576", "", "", "Beauty Salon", "Presque Isle", "Yes"),
        ("Hair & Beyond", "121 Parsons St", "Presque Isle", "ME", "04769", "(207) 764-1226", "", "", "Beauty Salon", "Presque Isle", "Yes"),
        ("For Paws Grooming", "141 Caribou Rd", "Presque Isle", "ME", "04769", "(207) 760-9501", "", "", "Pet Grooming", "Presque Isle", "Yes"),
        ("Shannon's Home Style Variety", "70 Academy St", "Presque Isle", "ME", "04769", "(207) 764-0713", "", "", "Convenience Store", "Presque Isle", "Yes"),
        ("Merchants on the Corner", "394 Main St", "Presque Isle", "ME", "04769", "(207) 764-1255", "", "", "Retail", "Presque Isle", "Yes"),
        ("The Olde Rustic Attic", "641 Main St", "Presque Isle", "ME", "04769", "(207) 764-5969", "", "", "Antiques", "Presque Isle", "Yes"),
        ("Second Chances Thrifts and Boutique", "159 State St", "Presque Isle", "ME", "04769", "(207) 227-3231", "", "", "Thrift Store", "Presque Isle", "Yes"),
        ("The Cubby Thrift Store", "377 Main St", "Presque Isle", "ME", "04769", "(207) 760-7070", "", "", "Thrift Store", "Presque Isle", "Yes"),
        # Fort Fairfield
        ("United Insurance", "263 Main St Suite 1", "Fort Fairfield", "ME", "04742", "(207) 472-3651", "", "", "Insurance", "Fort Fairfield", "Yes"),
        # Mars Hill
        ("The Rusty Crab", "48 Main St", "Mars Hill", "ME", "04758", "(207) 540-4343", "", "", "Restaurant", "Mars Hill", "No"),
        # Mapleton
        ("Mapleton Hardware", "1518 Main St", "Mapleton", "ME", "04757", "(207) 540-1700", "", "", "Hardware Store", "Mapleton", "Yes"),
        ("Main Street Hair Design", "1616 Main St", "Mapleton", "ME", "04757", "(207) 764-7600", "", "", "Hair Salon", "Mapleton", "Yes"),
        ("Chandler Farms Inc.", "1089 State Rd", "Mapleton", "ME", "04757", "(207) 764-5228", "", "", "Powersports Dealer", "Mapleton", "Yes"),
        ("Taste of Home Restaurant", "1701 Main St", "Mapleton", "ME", "04757", "(207) 768-3333", "", "", "Restaurant", "Mapleton", "No"),
        # Washburn
        ("Sally's Beauty Salon", "59 Cross Rd", "Washburn", "ME", "04786", "(207) 455-4059", "", "", "Beauty Salon", "Washburn", "Yes"),
        ("Aroostook Hospitality Inn", "23 Langille St", "Washburn", "ME", "04786", "(207) 455-8567", "", "", "Lodging", "Washburn", "Yes"),
        ("Katahdin Trust Company", "1282 Main St", "Washburn", "ME", "04786", "(207) 455-8141", "", "", "Bank", "Washburn", "Yes"),
        # Ashland
        ("Old Post Cafe", "101 Main St", "Ashland", "ME", "04732", "(207) 435-2902", "", "", "Restaurant", "Ashland", "No"),
        ("Art's Appliance & Furniture", "21 Main St A", "Ashland", "ME", "04732", "(207) 435-4151", "", "", "Appliance/Furniture", "Ashland", "Yes"),
        ("Gateway Trading Post Inc", "111 Garfield Rd", "Ashland", "ME", "04732", "(207) 435-6890", "", "", "General Store", "Ashland", "Yes"),
    ],
    'caribou_limestone': [
        # Caribou
        ("Ride North Harley-Davidson", "11 Laurette St", "Caribou", "ME", "04736", "(207) 496-3211", "", "", "Motorcycle Dealer", "Caribou", "Yes"),
        ("Quality Inn & Suites", "30 Access Hwy", "Caribou", "ME", "04736", "(207) 493-3311", "", "", "Hotel", "Caribou", "Yes"),
        ("Russell's Motel", "357 Main St", "Caribou", "ME", "04736", "(207) 498-2567", "", "", "Motel", "Caribou", "Yes"),
        ("Griffeth Mitsubishi", "16 Access Hwy", "Caribou", "ME", "04736", "(207) 496-3111", "", "", "Auto Dealer", "Caribou", "Yes"),
        ("Kieffer Real Estate", "101 High St", "Caribou", "ME", "04736", "(207) 498-2900", "", "", "Real Estate", "Caribou", "Yes"),
        ("Bernard-Coury Realty", "128 High St", "Caribou", "ME", "04736", "(207) 492-4571", "", "", "Real Estate", "Caribou", "Yes"),
        ("Progressive Realty", "45 Bennett Dr", "Caribou", "ME", "04736", "(207) 498-3848", "", "", "Real Estate", "Caribou", "Yes"),
        ("Russell-Clowes Insurance", "562 Main St", "Caribou", "ME", "04736", "(207) 496-6061", "", "", "Insurance", "Caribou", "Yes"),
        ("Gallagher Insurance Agency", "562 Main St", "Caribou", "ME", "04736", "(207) 498-8775", "", "", "Insurance", "Caribou", "Yes"),
        ("United Insurance", "101 High St", "Caribou", "ME", "04736", "(207) 496-3661", "", "", "Insurance", "Caribou", "Yes"),
        ("F.A. Peabody Insurance", "25 Sweden St STE C", "Caribou", "ME", "04736", "(207) 498-2523", "", "", "Insurance", "Caribou", "Yes"),
        ("H&R Block", "658 Main St Ste 3", "Caribou", "ME", "04736", "(207) 498-2561", "", "", "Tax Preparation", "Caribou", "Yes"),
        ("County Cuts", "539 Main St", "Caribou", "ME", "04736", "(207) 492-1102", "", "", "Barber Shop", "Caribou", "Yes"),
        ("Norseman Barbering Company", "118 Bennett Dr", "Caribou", "ME", "04736", "(207) 493-1021", "", "", "Barber Shop", "Caribou", "Yes"),
        ("Hair Affair", "169 High St STE C", "Caribou", "ME", "04736", "(207) 493-4470", "", "", "Beauty Salon", "Caribou", "Yes"),
        ("Home Sweet Salon", "203 Sweden St", "Caribou", "ME", "04736", "(207) 498-2229", "", "", "Beauty Salon", "Caribou", "Yes"),
        ("Shear Precision", "159 Bennett Dr", "Caribou", "ME", "04736", "(207) 492-7711", "", "", "Beauty Salon", "Caribou", "Yes"),
        ("Rose's Shear Magic", "46 Sweden St", "Caribou", "ME", "04736", "(207) 492-1200", "", "", "Beauty Salon", "Caribou", "Yes"),
        ("Vogue Salon", "137 Bennett Dr", "Caribou", "ME", "04736", "(207) 493-5342", "", "", "Beauty Salon", "Caribou", "Yes"),
        ("Serenity Beauty Spa", "11 Summer St", "Caribou", "ME", "04736", "(207) 492-2027", "", "", "Day Spa", "Caribou", "Yes"),
        ("Thrive Body Spa", "73 Sweden St", "Caribou", "ME", "04736", "(207) 496-0700", "", "", "Day Spa", "Caribou", "Yes"),
        ("Fox Den Tattoo", "342 Sweden St # B", "Caribou", "ME", "04736", "(207) 227-2804", "", "", "Tattoo Shop", "Caribou", "Yes"),
        ("Thistle Shop & Design", "26 Garden Cir", "Caribou", "ME", "04736", "(207) 498-1000", "", "", "Florist", "Caribou", "Yes"),
        ("Phil's Florist & Greenhouses", "358 Washburn St", "Caribou", "ME", "04736", "(207) 492-4241", "", "", "Florist/Greenhouse", "Caribou", "Yes"),
        ("Chadwick-BaRoss", "314 Main St", "Caribou", "ME", "04736", "(207) 498-2547", "", "", "Building Materials", "Caribou", "Yes"),
        ("AIM Recycling Caribou", "208 Limestone St", "Caribou", "ME", "04736", "(207) 492-1182", "", "", "Recycling Center", "Caribou", "No"),
        # Churches - Caribou
        ("Calvary Baptist Church", "46 Access Hwy", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Caribou Assembly of God", "116 Sweden St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Caribou Church of Christ", "9 Laurette Cir", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Caribou Seventh-day Adventist Church", "650 Main St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Caribou Ward (LDS)", "67 Paris Snow Dr", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Faith Lutheran Church", "18 Sweden St Ste 3", "Caribou", "ME", "04736", "(207) 498-8349", "", "", "Religion", "Caribou", "No"),
        ("Gray Memorial United Methodist Church", "2 Prospect St", "Caribou", "ME", "04736", "(207) 498-2103", "", "", "Religion", "Caribou", "No"),
        ("Holy Rosary Church", "34 Vaughn St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Jehovah's Witnesses Kingdom Hall", "596 Sweden St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Sacred Heart Church", "1143 Van Buren Rd", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("Saint Luke's Episcopal Church", "650 Main St", "Caribou", "ME", "04736", "(207) 492-4211", "", "", "Religion", "Caribou", "No"),
        ("Solid Rock Worship Center (United Pentecostal)", "133 Fort Fairfield Rd", "Caribou", "ME", "04736", "(207) 492-2436", "", "", "Religion", "Caribou", "No"),
        ("Caribou UU Congregation", "3 Grove St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        ("United Baptist Church", "74 High St", "Caribou", "ME", "04736", "", "", "", "Religion", "Caribou", "No"),
        # Non-church religious buildings - Caribou
        ("Threads of Hope Outlet (Catholic Charities)", "14 Old Van Buren Rd", "Caribou", "ME", "04736", "(207) 493-8919", "", "", "Religion", "Caribou", "Yes"),
        # Churches - Limestone
        ("Church of the Advent (Episcopal)", "Church St", "Limestone", "ME", "04750", "", "", "", "Religion", "Limestone", "No"),
        ("High Street Baptist Church", "70 High St", "Limestone", "ME", "04750", "(207) 325-4436", "", "", "Religion", "Limestone", "No"),
        ("Limestone United Methodist Church", "52 Main St", "Limestone", "ME", "04750", "(207) 325-4870", "", "", "Religion", "Limestone", "No"),
        # Limestone
        ("Nike Acres Bed & Breakfast", "57A Howard Rd", "Limestone", "ME", "04750", "(207) 540-5439", "", "", "Bed & Breakfast", "Limestone", "Yes"),
        ("Loring Air Museum", "161 Cupp Rd", "Limestone", "ME", "05151", "(207) 551-3439", "", "", "Museum", "Limestone", "No"),
        ("Limestone Snowhawks", "18 Grand Falls Rd", "Limestone", "ME", "04750", "(207) 498-0642", "", "", "Recreation", "Limestone", "No"),
    ],
    'houlton_region': [
        # Houlton
        ("Andy's IGA Foodliner", "132 North St", "Houlton", "ME", "04730", "(207) 532-3305", "", "", "Grocery Store", "Houlton", "Yes"),
        ("Pastry Corner", "51 Bangor St", "Houlton", "ME", "04730", "(207) 521-0026", "", "", "Bakery", "Houlton", "Yes"),
        ("Market Pizza", "23 Market Sq", "Houlton", "ME", "04730", "(207) 521-5045", "", "", "Restaurant", "Houlton", "No"),
        ("Tang's Chinese Cuisine", "60 North St", "Houlton", "ME", "04730", "(207) 532-9981", "", "", "Restaurant", "Houlton", "No"),
        ("Cold Stone Creamery", "290 North St", "Houlton", "ME", "04730", "(207) 521-0100", "", "", "Ice Cream", "Houlton", "Yes"),
        ("Tulgey Wood Emporium", "11 Court St", "Houlton", "ME", "04730", "(207) 521-5047", "", "", "Retail", "Houlton", "Yes"),
        ("Anciently Marked Tattoo Art Studio", "13 Court St", "Houlton", "ME", "04730", "", "", "", "Tattoo Shop", "Houlton", "Yes"),
        ("207 Collectibles", "17 Court St", "Houlton", "ME", "04730", "", "", "", "Collectibles", "Houlton", "Yes"),
        ("Bittersweet Thyme", "Main St", "Houlton", "ME", "04730", "", "", "", "Home Decor", "Houlton", "Yes"),
        ("Bittersweet Thyme Cafe", "Main St", "Houlton", "ME", "04730", "", "", "", "Coffee Shop", "Houlton", "Yes"),
        ("Riversbend Paddle Co.", "431 Bangor St", "Houlton", "ME", "04730", "(863) 273-2090", "", "", "Recreation", "Houlton", "No"),
        ("Cigaret Shopper", "", "Houlton", "ME", "04730", "", "", "", "Tobacco Shop", "Houlton", "Yes"),
        ("Serendipitous Dragonfly", "", "Houlton", "ME", "04730", "", "", "", "Retail", "Houlton", "Yes"),
        # Bridgewater
        ("Whited Bible Camp", "790 US-1", "Bridgewater", "ME", "04735", "(207) 429-9731", "", "", "Campground", "Bridgewater", "No"),
        # Island Falls
        ("Island Falls Opera House Inn & Lounge", "69 Burleigh St", "Island Falls", "ME", "04747", "(207) 694-2740", "", "", "Lodging/Restaurant", "Island Falls", "No"),
        ("North Gate Grill", "22 Houlton Rd", "Island Falls", "ME", "04747", "(207) 463-5012", "", "", "Restaurant", "Island Falls", "No"),
        ("Mimi's Cook Nook", "5 Nina Sawyer Ln", "Island Falls", "ME", "04747", "", "", "", "Restaurant", "Island Falls", "No"),
        # Hodgdon
        ("Anderson's Mill Pond Dairy Bar", "226 Hodgdon Mills Rd", "Hodgdon", "ME", "04730", "(207) 532-9891", "", "", "Ice Cream", "Hodgdon", "Yes"),
        # Monticello
        ("Blue Moose Restaurant", "180 US-1", "Monticello", "ME", "04760", "(207) 538-0991", "", "", "Restaurant", "Monticello", "No"),
        # New Limerick
        ("Lakeside Restaurant", "6 Country Club Dr", "New Limerick", "ME", "04761", "(207) 694-9494", "", "", "Restaurant", "New Limerick", "No"),
        ("Carol's Country Yarns", "1087 County Rd", "New Limerick", "ME", "04761", "", "", "", "Yarn/Craft Shop", "New Limerick", "Yes"),
        # Oakfield
        ("A Place to Eat", "260 Oakfield Smyrna Rd", "Oakfield", "ME", "04763", "(207) 757-7474", "", "", "Restaurant", "Oakfield", "No"),
        # Dyer Brook
        ("Midnight Auto Repair", "56 Keith Brook Rd", "Dyer Brook", "ME", "04747", "(207) 757-8726", "", "", "Auto Repair", "Dyer Brook", "No"),
        # Churches - Houlton
        ("St. Mary of the Visitation Catholic Church", "110 Military St", "Houlton", "ME", "04730", "(207) 532-2871", "", "", "Religion", "Houlton", "No"),
        ("First Baptist Church of Houlton", "46 Court St", "Houlton", "ME", "04730", "(207) 532-3196", "", "", "Religion", "Houlton", "No"),
        ("Military Street Baptist Church", "307 Military St", "Houlton", "ME", "04730", "(207) 532-2783", "", "", "Religion", "Houlton", "No"),
        ("Houlton United Methodist Church", "57 Military St", "Houlton", "ME", "04730", "(207) 532-3332", "", "", "Religion", "Houlton", "No"),
        ("Cornerstone Baptist Church", "16 Columbia St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Shiretown Baptist Church", "4 Randall Ct", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Unitarian Society of Houlton", "61 Military St", "Houlton", "ME", "04730", "(207) 532-3320", "", "", "Religion", "Houlton", "No"),
        ("Church of the Nazarene", "11 Hogan St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Church of Christ", "140 Main St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Houlton Wesleyan Church", "18 Kelleran St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Houlton Christian Science Society", "5 Heywood St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Full Gospel Assembly", "200 Court St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("LDS Church (Houlton Branch)", "10 Pleasant St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Kingdom Hall of Jehovah's Witnesses", "576 Smyrna St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Salvation Army", "12 Court St", "Houlton", "ME", "04730", "(207) 532-2322", "", "", "Religion", "Houlton", "No"),
        ("First Congregational Church", "45 High St", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        ("Amity Baptist Church", "62 Pearce Ave", "Houlton", "ME", "04730", "", "", "", "Religion", "Houlton", "No"),
        # Churches - Island Falls
        ("United Baptist Church", "Burleigh St", "Island Falls", "ME", "04747", "(207) 463-2224", "", "", "Religion", "Island Falls", "No"),
        ("Whittier Congregational Church", "Whittier Rd", "Island Falls", "ME", "04747", "(207) 463-2208", "", "", "Religion", "Island Falls", "No"),
        ("St. Agnes Catholic Church", "76 Sewall St", "Island Falls", "ME", "04747", "(207) 532-2871", "", "", "Religion", "Island Falls", "No"),
        # Churches - Oakfield
        ("Bethel Church", "111 Oakfield Smyrna Rd", "Oakfield", "ME", "04763", "(207) 447-0759", "", "", "Religion", "Oakfield", "No"),
        # Churches - Hodgdon
        ("Hodgdon United Methodist Church", "US-1", "Hodgdon", "ME", "04730", "", "", "", "Religion", "Hodgdon", "No"),
        ("New Life Assembly of God", "39 Hodgdon Mills Rd", "Hodgdon", "ME", "04730", "", "", "", "Religion", "Hodgdon", "No"),
        # Churches - Bridgewater
        ("Whited Bible Camp", "790 US-1", "Bridgewater", "ME", "04735", "(207) 429-9731", "", "", "Religion", "Bridgewater", "No"),
        # Churches - Monticello
        ("Monticello Baptist Church", "Main St", "Monticello", "ME", "04760", "", "", "", "Religion", "Monticello", "No"),
        # Non-church religious buildings - Houlton
        ("Salvation Army Family Thrift Store", "65 Main St", "Houlton", "ME", "04730", "(207) 521-0230", "", "", "Religion", "Houlton", "Yes"),
        # Non-church religious buildings - Monticello
        ("Threads of Hope Outlet (Catholic Charities)", "163 US Route 1", "Monticello", "ME", "04760", "(207) 493-8919", "", "", "Religion", "Monticello", "Yes"),
        # Churches - Linneus
        ("Linneus Church", "824 Foxcroft Rd", "Linneus", "ME", "04730", "", "", "", "Religion", "Linneus", "No"),
        # Churches - Littleton
        ("Littleton Baptist Church", "Main St", "Littleton", "ME", "04730", "", "", "", "Religion", "Littleton", "No"),
        # Churches - Smyrna
        ("Smyrna Baptist Church", "1086 Smyrna Rd", "Smyrna", "ME", "04730", "", "", "", "Religion", "Smyrna", "No"),
        # Churches - New Limerick
        ("New Limerick Baptist Church", "County Rd", "New Limerick", "ME", "04761", "", "", "", "Religion", "New Limerick", "No"),
        # Churches - Dyer Brook
        ("Dyer Brook Union Church", "6 Dyer Brook Rd", "Dyer Brook", "ME", "04747", "", "", "", "Religion", "Dyer Brook", "No"),
    ],
    'millinocket_area': [
        # Millinocket
        ("Sawmill Bar & Grill", "9 Millinocket Lake Rd", "Millinocket", "ME", "04462", "(207) 447-6996", "", "", "Restaurant/Bar", "Millinocket", "No"),
        ("Millinocket Army Navy Store", "140 Penobscot Ave", "Millinocket", "ME", "04462", "(207) 723-8588", "", "", "Retail", "Millinocket", "Yes"),
        ("Millinocket Furniture Co", "31 Hemlock St", "Millinocket", "ME", "04462", "(207) 723-5335", "", "", "Furniture Store", "Millinocket", "Yes"),
        ("Young House Bed & Breakfast", "193 Central St", "Millinocket", "ME", "04462", "(207) 723-5452", "", "", "Bed & Breakfast", "Millinocket", "Yes"),
        ("Abol Bridge Campground & Store", "3969 Golden Rd", "Millinocket", "ME", "04462", "(207) 447-5803", "", "", "Campground/Store", "Millinocket", "Yes"),
        # East Millinocket
        ("Main Street Floral & Gift Shop", "67 Main St", "East Millinocket", "ME", "04430", "(207) 746-0044", "", "", "Florist/Gifts", "East Millinocket", "Yes"),
        ("Forget Me Not Shoppe", "117 Main St", "East Millinocket", "ME", "04430", "(207) 746-9250", "", "", "Florist/Gifts", "East Millinocket", "Yes"),
        # Medway
        ("Country Diner", "2202 Medway Rd", "Medway", "ME", "04460", "(207) 746-9343", "", "", "Restaurant", "Medway", "No"),
        ("Big Apple Convenience Store", "2202 Medway Rd", "Medway", "ME", "04460", "(207) 746-5966", "", "", "Convenience Store/Gas", "Medway", "Yes"),
        ("Katahdin General - Medway", "2309 Medway Rd", "Medway", "ME", "04460", "(207) 746-5336", "", "", "General Store", "Medway", "Yes"),
        # Sherman
        ("Brenda's Restaurant", "98 Main St", "Sherman", "ME", "04776", "(207) 365-4773", "", "", "Restaurant", "Sherman", "No"),
        ("F.A. Peabody Insurance", "16 Station Rd", "Sherman", "ME", "04776", "(207) 365-4238", "", "", "Insurance", "Sherman", "Yes"),
        # Patten
        ("Patten Drug LLC", "20 Main St", "Patten", "ME", "04765", "(207) 528-2244", "", "", "Pharmacy", "Patten", "Yes"),
        ("Milliken Medical Center", "17 Founders St", "Patten", "ME", "04765", "(207) 528-2067", "", "", "Medical", "Patten", "No"),
        # Mount Chase
        ("Back Wood BBQ", "76 Mountain Rd", "Mount Chase", "ME", "04765", "(207) 538-8146", "", "", "Restaurant", "Mount Chase", "No"),
        # Shin Pond
        ("Shin Pond Pub", "1149 Shin Pond Rd", "Mount Chase", "ME", "04765", "(207) 528-2660", "", "", "Restaurant/Bar", "Shin Pond", "No"),
        # Churches - Millinocket
        ("Millinocket Church of the Nazarene", "135 Forest Ave", "Millinocket", "ME", "04462", "(207) 723-4533", "", "", "Religion", "Millinocket", "No"),
        ("Faith Baptist Church", "244 Massachusetts Ave", "Millinocket", "ME", "04462", "(207) 723-5580", "", "", "Religion", "Millinocket", "No"),
        ("Millinocket Baptist Church", "297 Penobscot Ave", "Millinocket", "ME", "04462", "(207) 723-4862", "", "", "Religion", "Millinocket", "No"),
        ("St. Martin of Tours Catholic Church", "19 Colby St", "Millinocket", "ME", "04462", "(207) 723-5902", "", "", "Religion", "Millinocket", "No"),
        ("St. Andrew's Episcopal Church", "40 Highland Ave", "Millinocket", "ME", "04462", "(207) 723-5893", "", "", "Religion", "Millinocket", "No"),
        ("First Congregational Church", "274 Katahdin Ave", "Millinocket", "ME", "04462", "(207) 723-5591", "", "", "Religion", "Millinocket", "No"),
        ("Your Family Worship Center (First Pentecostal)", "100 Aroostook Ave", "Millinocket", "ME", "04462", "(207) 723-6223", "", "", "Religion", "Millinocket", "No"),
        ("Charleston Church Katahdin", "11 Tamarack St", "Millinocket", "ME", "04462", "", "", "", "Religion", "Millinocket", "No"),
        # Churches - East Millinocket
        ("Calvary Temple Assembly of God", "2 Orchard St", "East Millinocket", "ME", "04430", "(207) 746-5274", "", "", "Religion", "East Millinocket", "No"),
        ("First Baptist Church", "2 Oak St", "East Millinocket", "ME", "04430", "(207) 746-5185", "", "", "Religion", "East Millinocket", "No"),
        ("First Congregational Church (East Millinocket)", "11 Maple St", "East Millinocket", "ME", "04430", "(207) 746-5575", "", "", "Religion", "East Millinocket", "No"),
        ("Living Hope Church of the Nazarene", "1 Palm St", "East Millinocket", "ME", "04430", "(207) 746-3760", "", "", "Religion", "East Millinocket", "No"),
        ("St. Peter's Catholic Church", "58 Cedar St", "East Millinocket", "ME", "04430", "(207) 746-3333", "", "", "Religion", "East Millinocket", "No"),
        ("Tri Town Baptist Church", "8 Cone St", "East Millinocket", "ME", "04430", "(207) 746-2211", "", "", "Religion", "East Millinocket", "No"),
        # Churches - Medway
        ("Glad Tidings Church of God", "2181 Medway Rd", "Medway", "ME", "04460", "(207) 746-5304", "", "", "Religion", "Medway", "No"),
        # Churches - Sherman
        ("Washburn Memorial Church (UCC)", "3 Church St", "Sherman", "ME", "04776", "(207) 365-4664", "", "", "Religion", "Sherman", "No"),
        ("Monarda Calvary Baptist Church", "1301 Silver Ridge Rd", "Sherman", "ME", "04776", "(207) 365-4043", "", "", "Religion", "Sherman", "No"),
        # Churches - Patten
        ("St. Paul's Catholic Church", "34 Katahdin St", "Patten", "ME", "04765", "(207) 532-2871", "", "", "Religion", "Patten", "No"),
        ("Patten Pentecostal Church (Assemblies of God)", "101 Main St", "Patten", "ME", "04765", "(207) 528-2512", "", "", "Religion", "Patten", "No"),
        ("Stetson Memorial United Methodist Church", "7 Houlton St", "Patten", "ME", "04765", "(207) 528-2277", "", "", "Religion", "Patten", "No"),
    ],
    'lincoln_area': [
        # Lincoln
        ("Pat's Pizza", "237 Main St", "Lincoln", "ME", "04457", "(207) 794-2211", "", "", "Restaurant", "Lincoln", "No"),
        ("Lincoln House of Pizza", "38 Main St", "Lincoln", "ME", "04457", "(207) 794-2526", "", "", "Restaurant", "Lincoln", "No"),
        ("Wing Wah Restaurant", "60 Main St", "Lincoln", "ME", "04457", "(207) 794-3001", "", "", "Restaurant", "Lincoln", "No"),
        ("Subway", "115 W Broadway", "Lincoln", "ME", "04457", "(207) 794-2008", "", "", "Restaurant", "Lincoln", "No"),
        ("Wendy's", "184 W Broadway", "Lincoln", "ME", "04457", "(207) 403-9011", "", "", "Restaurant", "Lincoln", "No"),
        ("Dunkin' Donuts", "142 W Broadway", "Lincoln", "ME", "04457", "(207) 794-2154", "", "", "Coffee Shop", "Lincoln", "Yes"),
        ("Ninja Express Japanese Steakhouse", "86 W Broadway", "Lincoln", "ME", "04457", "(207) 407-9031", "", "", "Restaurant", "Lincoln", "No"),
        ("Gather Brunch & Bar", "1 Fleming St", "Lincoln", "ME", "04457", "(207) 403-9403", "", "", "Restaurant", "Lincoln", "No"),
        ("Lincoln Tap House", "222 W Broadway", "Lincoln", "ME", "04457", "(207) 403-9116", "", "", "Restaurant/Bar", "Lincoln", "No"),
        ("The Forester Pub", "204 W Broadway", "Lincoln", "ME", "04457", "(207) 403-9224", "", "", "Restaurant/Bar", "Lincoln", "No"),
        ("Charlie's Seafood Market", "20 School St", "Lincoln", "ME", "04457", "(207) 794-3100", "", "", "Seafood Market", "Lincoln", "Yes"),
        ("Gillmor's Restaurant & Lounge", "236 W Broadway", "Lincoln", "ME", "04457", "(207) 794-6565", "", "", "Restaurant", "Lincoln", "No"),
        ("Linda's Hair Care", "3 Katahdin Ave", "Lincoln", "ME", "04457", "(207) 794-0254", "", "", "Hair Salon", "Lincoln", "Yes"),
        ("Keys'n Things", "22 Taylor St", "Lincoln", "ME", "04457", "(207) 794-6833", "", "", "Locksmith", "Lincoln", "Yes"),
        ("Transitions Hair & Tanning", "104 Main St", "Lincoln", "ME", "04457", "(207) 794-0909", "", "", "Salon", "Lincoln", "Yes"),
        ("Goldstar Cleaners", "120 Main St", "Lincoln", "ME", "04457", "(207) 989-5170", "", "", "Dry Cleaner", "Lincoln", "Yes"),
        ("JaTo Highlands Golf Course", "175 Town Farm Rd", "Lincoln", "ME", "04457", "(207) 794-2433", "", "", "Golf Course", "Lincoln", "No"),
        ("Stewart Professional Learning Center & CoWork", "51 Main St", "Lincoln", "ME", "04457", "(207) 290-0956", "", "", "Business Center", "Lincoln", "Yes"),
        # Howland
        ("Handy Stop", "2 Bridge St", "Howland", "ME", "04448", "(207) 732-5274", "", "", "Convenience Store/Gas", "Howland", "Yes"),
        # Enfield
        ("Montague Public House", "76 Bridge St", "Enfield", "ME", "04493", "(207) 732-4943", "", "", "Restaurant/Bar", "Enfield", "No"),
        # Chester
        ("Furever Friends Doggie Daycare", "3 Mattamiscontis Rd", "Chester", "ME", "04457", "(207) 290-7756", "", "", "Pet Services", "Chester", "Yes"),
        # Winn
        ("Berry Land Take Out", "990 US-2", "Winn", "ME", "04495", "(207) 736-4775", "", "", "Take Out Restaurant", "Winn", "No"),
        ("Winn General Store", "985 US-2", "Winn", "ME", "04495", "(207) 736-4068", "", "", "General Store", "Winn", "Yes"),
        # Mattawamkeag
        ("Crossroads Restaurant & Motel", "270 Main St", "Mattawamkeag", "ME", "04459", "(207) 736-3020", "", "", "Restaurant/Motel", "Mattawamkeag", "No"),
        ("Markie's Pizza Joint", "387 N Main St", "Mattawamkeag", "ME", "04459", "(207) 736-2029", "", "", "Restaurant", "Mattawamkeag", "No"),
        ("Waggin Tails Pet SPA", "405 Main St", "Mattawamkeag", "ME", "04459", "(207) 736-4891", "", "", "Pet Grooming", "Mattawamkeag", "Yes"),
        # Springfield
        ("Grammy Anna's", "7 Park St", "Springfield", "ME", "04487", "(207) 765-9683", "", "", "Take Out Restaurant", "Springfield", "No"),
        # Lee
        ("House in the Woods", "217 Skunk Hill Rd", "Lee", "ME", "04455", "(207) 738-8387", "", "", "Nonprofit Retreat", "Lee", "No"),
        # Churches - Lincoln
        ("First Congregational Church of Lincoln (UCC)", "19 School St", "Lincoln", "ME", "04457", "(207) 794-6613", "", "", "Religion", "Lincoln", "No"),
        ("First United Methodist Church of Lincoln", "8 Lee Rd", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("St. Mary of Lourdes Church (Catholic)", "142 Main St", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("Lincoln Seventh-day Adventist Church", "158 River Rd", "Lincoln", "ME", "04457", "(207) 794-3361", "", "", "Religion", "Lincoln", "No"),
        ("Bible Baptist Church of Lincoln", "53 Fleming St", "Lincoln", "ME", "04457", "(207) 794-6650", "", "", "Religion", "Lincoln", "No"),
        ("Full Gospel Tabernacle", "14 Fleming St", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("Lincoln Center Church of God", "497 Main St", "Lincoln", "ME", "04457", "(207) 746-7287", "", "", "Religion", "Lincoln", "No"),
        ("Maranatha Riverside Church", "176 River Rd", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("LDS Church (Lincoln Branch)", "144 Penobscot Valley Ave", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("Kingdom Hall of Jehovah's Witnesses", "343 West Broadway", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        ("Lincoln Center Baptist Church", "323 Main St", "Lincoln", "ME", "04457", "", "", "", "Religion", "Lincoln", "No"),
        # Churches - Howland
        ("Howland Baptist Church", "5 Penobscot Ave", "Howland", "ME", "04448", "(207) 732-3170", "", "", "Religion", "Howland", "No"),
        ("St. Leo the Great Church (Catholic)", "18 River Rd", "Howland", "ME", "04448", "(207) 732-3495", "", "", "Religion", "Howland", "No"),
        # Churches - Enfield
        ("Enfield Baptist Church", "7 Lincoln Rd", "Enfield", "ME", "04493", "(207) 732-4200", "", "", "Religion", "Enfield", "No"),
        ("West Enfield Church of God", "West Enfield", "Enfield", "ME", "04493", "(207) 732-4410", "", "", "Religion", "Enfield", "No"),
        # Churches - Burlington
        ("Burlington Baptist Church", "18 Church Hill Rd", "Burlington", "ME", "04417", "(207) 732-3778", "", "", "Religion", "Burlington", "No"),
        # Churches - Chester
        ("Chester Baptist Church", "2 S Chester Rd", "Chester", "ME", "04457", "(207) 746-3650", "", "", "Religion", "Chester", "No"),
        # Churches - Winn
        ("St. Thomas Episcopal Church", "14 Main St", "Winn", "ME", "04495", "(207) 736-2010", "", "", "Religion", "Winn", "No"),
        ("Sacred Heart Church (Catholic)", "Lee-Winn Rd", "Winn", "ME", "04495", "(207) 794-6333", "", "", "Religion", "Winn", "No"),
        # Churches - Mattawamkeag
        ("Mattawamkeag United Methodist Church", "14 Depot St", "Mattawamkeag", "ME", "04459", "", "", "", "Religion", "Mattawamkeag", "No"),
        ("Mattawamkeag Church of God", "284 Main St", "Mattawamkeag", "ME", "04459", "(207) 736-7676", "", "", "Religion", "Mattawamkeag", "No"),
        ("Mattawamkeag Baptist Church", "209 S Main St", "Mattawamkeag", "ME", "04459", "(207) 736-4791", "", "", "Religion", "Mattawamkeag", "No"),
        ("Zion Pentecostal Church", "249 Medway Rd", "Mattawamkeag", "ME", "04459", "(207) 736-7655", "", "", "Religion", "Mattawamkeag", "No"),
        # Churches - Lee
        ("Lee Baptist Church", "2870 Lee Rd", "Lee", "ME", "04455", "(207) 738-2747", "", "", "Religion", "Lee", "No"),
        ("Christian and Missionary Alliance Church of Lee", "249 Winn Rd", "Lee", "ME", "04455", "(207) 738-4508", "", "", "Religion", "Lee", "No"),
        # Churches - Springfield
        ("Springfield Congregational Church (UCC)", "970 Main St", "Springfield", "ME", "04487", "(207) 738-2155", "", "", "Religion", "Springfield", "No"),
        # Churches - Greenbush
        ("Olamon Faith Bible Church", "102 Military Rd", "Greenbush", "ME", "04418", "(207) 826-2179", "", "", "Religion", "Greenbush", "No"),
        ("Cardville United Pentecostal Church", "144 Cards Ridge Rd", "Greenbush", "ME", "04418", "(207) 827-7763", "", "", "Religion", "Greenbush", "No"),
        # Churches - Lowell
        ("Lowell Baptist Church", "Church St", "Lowell", "ME", "04493", "", "", "", "Religion", "Lowell", "No"),
    ],
}

REGION_FILES = {
    'presque_isle_area': 'cleaned/presque_isle_area.csv',
    'caribou_limestone': 'cleaned/caribou_limestone.csv',
    'houlton_region': 'cleaned/houlton_region.csv',
    'millinocket_area': 'cleaned/millinocket_area.csv',
    'lincoln_area': 'cleaned/lincoln_area.csv',
}

FIELD_NAMES = ['Business Name', 'Street Address', 'City', 'State', 'Zip',
               'Phone', 'Email', 'Website', 'Category', 'Town', 'SuitableForAds']

total_added = 0
total_skipped = 0

for region_key, csv_path in REGION_FILES.items():
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        old_fn = reader.fieldnames

    existing = set()
    for r in rows:
        key = (r['Business Name'].strip().lower(), r.get('Town', '').strip().lower())
        existing.add(key)

    new_rows = []
    added = 0
    for entry in MISSING.get(region_key, []):
        name, address, city, state, zipcode, phone, email, website, category, town, suitable = entry
        key = (name.strip().lower(), town.strip().lower())
        if key in existing:
            total_skipped += 1
            continue
        new_rows.append({
            'Business Name': name,
            'Street Address': address,
            'City': city,
            'State': state,
            'Zip': zipcode,
            'Phone': phone,
            'Email': email,
            'Website': website,
            'Category': category,
            'Town': town,
            'SuitableForAds': suitable,
        })
        added += 1
        existing.add(key)

    # Write new CSV with SuitableForAds column
    rows.extend(new_rows)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        # Ensure all rows have SuitableForAds field
        for r in rows:
            if 'SuitableForAds' not in r:
                r['SuitableForAds'] = ''
            # Write only our field names
            writer.writerow({k: r.get(k, '') for k in FIELD_NAMES})

    total_added += added
    print(f"{region_key}: +{added} businesses (total: {len(rows)}, skipped {len(MISSING.get(region_key, [])) - added})")

print(f"\nTotal added across all regions: {total_added}")
print(f"Total skipped (already existed): {total_skipped}")
