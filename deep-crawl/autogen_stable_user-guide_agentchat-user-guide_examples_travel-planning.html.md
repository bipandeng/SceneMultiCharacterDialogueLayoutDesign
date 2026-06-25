<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/examples/travel-planning.html -->

# Travel Planning#

在本示例中，我们将逐步介绍使用 AgentChat 创建复杂的旅行规划系统的过程。我们的旅行规划器将利用多个 AI 代理，每个代理都有特定的角色，协作创建一份全面的旅行行程。

首先，让我们导入必要的模块。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    

## Defining Agents#

在下一节中，我们将定义将在旅行规划团队中使用的代理。
    
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
    planner_agent = AssistantAgent(
        "planner_agent",
        model_client=model_client,
        description="A helpful assistant that can plan trips.",
        system_message="You are a helpful assistant that can suggest a travel plan for a user based on their request.",
    )
    
    local_agent = AssistantAgent(
        "local_agent",
        model_client=model_client,
        description="A local assistant that can suggest local activities or places to visit.",
        system_message="You are a helpful assistant that can suggest authentic and interesting local activities or places to visit for a user and can utilize any context information provided.",
    )
    
    language_agent = AssistantAgent(
        "language_agent",
        model_client=model_client,
        description="A helpful assistant that can provide language tips for a given destination.",
        system_message="You are a helpful assistant that can review travel plans, providing feedback on important/critical tips about how best to address language or communication challenges for the given destination. If the plan already includes language tips, you can mention that the plan is satisfactory, with rationale.",
    )
    
    travel_summary_agent = AssistantAgent(
        "travel_summary_agent",
        model_client=model_client,
        description="A helpful assistant that can summarize the travel plan.",
        system_message="You are a helpful assistant that can take in all of the suggestions and advice from the other agents and provide a detailed final travel plan. You must ensure that the final plan is integrated and complete. YOUR FINAL RESPONSE MUST BE THE COMPLETE PLAN. When the plan is complete and all perspectives are integrated, you can respond with TERMINATE.",
    )
    
    
    
    termination = TextMentionTermination("TERMINATE")
    group_chat = RoundRobinGroupChat(
        [planner_agent, local_agent, language_agent, travel_summary_agent], termination_condition=termination
    )
    await Console(group_chat.run_stream(task="Plan a 3 day trip to Nepal."))
    
    await model_client.close()
    
    
    
    ---------- user ----------
    Plan a 3 day trip to Nepal.
    ---------- planner_agent ----------
    Nepal is a stunning destination with its rich cultural heritage, breathtaking landscapes, and friendly people. A 3-day trip to Nepal is short, so let's focus on maximizing your experience with a mix of cultural, adventure, and scenic activities. Here's a suggested itinerary:
    
    ### Day 1: Arrival in Kathmandu
    - **Morning:**
      - Arrive at Tribhuvan International Airport in Kathmandu.
      - Check into your hotel and freshen up.
    - **Late Morning:**
      - Visit **Swayambhunath Stupa** (also known as the Monkey Temple). This ancient religious site offers a panoramic view of the Kathmandu Valley.
    - **Afternoon:**
      - Head to **Kathmandu Durbar Square** to explore the old royal palace and various temples. Don't miss the Kumari Ghar, which is home to the living goddess.
      - Have lunch at a nearby local restaurant and try traditional Nepali cuisine.
    - **Evening:**
      - Explore the vibrant streets of **Thamel**, a popular tourist district with shops, restaurants, and markets.
      - Dinner at a cozy restaurant featuring Nepali or continental dishes.
    
    ### Day 2: Day Trip to Patan and Bhaktapur
    - **Morning:**
      - Drive to **Patan (Lalitpur)**, only a few kilometers from Kathmandu. Explore **Patan Durbar Square** with its incredible temples and ancient palaces.
    - **Late Morning:**
      - Visit the **Patan Museum** for its unique collection of artifacts.
      - Optional: Visit the nearby **Golden Temple (Hiranya Varna Mahavihar)**.
    - **Afternoon:**
      - Head to **Bhaktapur**, about an hour's drive from Patan. Visit **Bhaktapur Durbar Square**, known for its medieval art and architecture.
      - Try some local **"juju dhau"** (king curd) – a must-taste in Bhaktapur.
    - **Evening:**
      - Return to Kathmandu for an evening of relaxation.
      - Dinner at a restaurant with cultural performances, such as traditional Nepali dance.
    
    ### Day 3: Nature Excursion and Departure
    - **Early Morning:**
      - If interested in a short trek, consider a half-day hike to **Nagarkot** for sunrise views over the Himalayas. This requires an early start (leave around 4 AM). You can also enjoy a hearty breakfast with a view.
    - **Late Morning:**
      - Return to Kathmandu. If trekking to Nagarkot isn't feasible, visit the **Pashupatinath Temple**, a UNESCO World Heritage site, or the nearby **Boudhanath Stupa**.
    - **Afternoon:**
      - Visit the **Garden of Dreams** for some tranquility before departure. It's a beautifully restored, serene garden.
    - **Evening:**
      - Depending on your flight schedule, enjoy some last-minute shopping or relishing Nepali momos (dumplings) before you head to the airport.
    - **Departure:**
      - Transfer to Tribhuvan International Airport for your onward journey.
    
    ### Tips:
    - Check the weather and prepare accordingly, especially if visiting during the monsoon or winter.
    - Respect local customs and traditions, especially when visiting religious sites. Dress modestly and be mindful of photography rules.
    - Consider adjusting this itinerary based on your arrival and departure times and personal interests.
    
    I hope you have an unforgettable experience in Nepal! Safe travels!
    [Prompt tokens: 40, Completion tokens: 712]
    ---------- local_agent ----------
    Nepal offers a blend of natural beauty, rich culture, and historical wonders. For a condensed yet fulfilling 3-day trip, the following itinerary focuses on providing a diverse taste of what Nepal has to offer:
    
    ### Day 1: Explore Kathmandu
    - **Morning:**
      - Arrive at Tribhuvan International Airport.
      - Check into your hotel and rest or freshen up.
    - **Late Morning:**
      - Visit **Swayambhunath Stupa** (Monkey Temple) for panoramic views and insight into Nepalese spirituality.
    - **Afternoon:**
      - Explore **Kathmandu Durbar Square**, where you can admire historic palaces and temples.
      - Have lunch nearby and try traditional Nepali dishes like dal bhat (lentils and rice).
    - **Evening:**
      - Stroll through **Thamel**, a lively district filled with shops and restaurants.
      - Enjoy dinner at a cultural restaurant featuring a traditional Nepali dance show.
    
    ### Day 2: Discover Patan and Bhaktapur
    - **Morning:**
      - Head to **Patan** to explore **Patan Durbar Square**, known for its stunning Newar architecture.
      - Visit the **Patan Museum** to learn about Nepalese history and art.
      - Optional: Visit the **Golden Temple (Hiranya Varna Mahavihar)**.
    - **Afternoon:**
      - Travel to **Bhaktapur**, a medieval town famous for its well-preserved architecture.
      - Visit **Bhaktapur Durbar Square** and enjoy the artistic temples and palaces.
      - Savor local specialties like **"juju dhau"** (king curd).
    - **Evening:**
      - Return to Kathmandu for dinner and relaxation.
    
    ### Day 3: Nature and Spirituality
    - **Early Morning:**
      - Depart for **Nagarkot** to catch the sunrise over the Himalayas, offering breathtaking views of peaks including Mount Everest. If possible, enjoy breakfast with the scenic backdrop.
    - **Late Morning:**
      - Return to Kathmandu. Alternatively, visit the **Pashupatinath Temple**, one of Nepal's holiest Hindu sites.
    - **Afternoon:**
      - See the majestic **Boudhanath Stupa**, one of the largest stupas in the world.
      - Relax in the **Garden of Dreams**, a peaceful oasis in the city.
    - **Evening:**
      - Enjoy a final meal featuring local favorites such as momos (dumplings) before heading to the airport.
    - **Departure:**
      - Transfer to Tribhuvan International Airport for your departure.
    
    ### Tips:
    - Dress modestly and be respectful when visiting religious sites.
    - Adjust the itinerary based on your interests and flight times.
    - Consider the weather; pack appropriately for the season.
    
    This itinerary offers a snapshot of Nepal's diverse attractions, blending cultural immersion with natural beauty. Wishing you a memorable trip! Safe travels!
    [Prompt tokens: 768, Completion tokens: 604]
    ---------- language_agent ----------
    Your 3-day trip to Nepal is well-planned, giving you a taste of the country's vibrant culture, rich history, and breathtaking landscapes. Here are some important language and communication tips that will enhance your experience:
    
    1. **Basic Nepali Phrases**: While English is widely spoken in tourist areas, learning a few basic Nepali phrases can be helpful and appreciated by locals. Here are some to consider:
       - Namaste (नमस्ते) – Hello
       - Dhanyabad (धन्यवाद) – Thank you
       - Mitho cha (मिठो छ) – It's delicious
       - Kripya (कृपया) – Please
       - Maaph garnus (माफ गर्नुहोस्) – Sorry/Excuse me
    
    2. **Gesture Understanding**: In Nepal, the slight tilting head nod means "yes," and shaking your head left to right can mean "no." This might be different from some Western countries where nodding generally signifies agreement.
    
    3. **Respect and Etiquette**: When visiting religious sites, remove shoes and hats before entering. It's respectful to use your right hand when giving or receiving something, as the left hand is considered impure in Nepali culture.
    
    4. **Offline Translation Apps**: Consider downloading an offline translation app or phrasebook in case you find yourself in areas where English might not be as common.
    
    5. **Non-Verbal Communication**: A smile goes a long way in Nepal. If you encounter a language barrier, hand gestures and a friendly demeanor can be very effective.
    
    With these tips in mind, your itinerary seems well-rounded, giving you a rich experience in Nepal. Enjoy your trip and the diverse experiences Nepal has to offer!
    [Prompt tokens: 1403, Completion tokens: 353]
    ---------- travel_summary_agent ----------
    Here's your comprehensive and integrated 3-day travel plan for an unforgettable trip to Nepal. This itinerary focuses on delivering a taste of Nepal's culture, history, nature, and hospitality, while incorporating practical language and cultural tips to enhance your experience.
    
    ### Day 1: Arrival and Cultural Exploration in Kathmandu
    - **Morning:**
      - Arrive at Tribhuvan International Airport in Kathmandu. Begin your adventure by checking into your hotel to rest and freshen up.
    - **Late Morning:**
      - Explore **Swayambhunath Stupa** (Monkey Temple), a symbolic and spiritual site offering magnificent panoramic views of the Kathmandu Valley. Learn basic Nepali phrases like "Namaste" to greet locals warmly.
    - **Afternoon:**
      - Visit the historic **Kathmandu Durbar Square** to admire the old royal palace and the surrounding temples, including the Kumari Ghar, home to the living goddess.
      - Have lunch at a nearby restaurant and try dishes like dal bhat to get a flavor of traditional Nepali cuisine.
    - **Evening:**
      - Stroll through the vibrant streets of **Thamel**, a hub for tourists with many shops and eateries. Use simple gestures and smiles as you interact with local shopkeepers.
      - Enjoy dinner at a restaurant with cultural performances, including traditional Nepali dance. Practice "Dhanyabad" to show appreciation.
    
    ### Day 2: Discovering Heritage in Patan and Bhaktapur
    - **Morning:**
      - Travel to **Patan** to explore the beautiful **Patan Durbar Square** and the **Patan Museum**, marveling at its rich Newar architecture and extensive collection of artifacts.
      - Optionally, visit the nearby **Golden Temple (Hiranya Varna Mahavihar)**.
    - **Afternoon:**
      - Head to the ancient city of **Bhaktapur**, around an hour's drive from Patan. Visit **Bhaktapur Durbar Square**, known for its well-preserved pagodas and temples.
      - Relish the local specialty, **"juju dhau"** (king curd), an unmissable treat in Bhaktapur.
      - Use polite phrases like "Kripya" (please) and "Maaph garnus" (excuse me) during interactions.
    - **Evening:**
      - Return to Kathmandu for dinner and unwind. Embrace the gentle head nod culture when communicating to show understanding and respect.
    
    ### Day 3: Embracing Nature and Spirituality
    - **Early Morning:**
      - Venture to **Nagarkot** early to catch the breathtaking sunrise over the Himalayas. Savor a hearty breakfast amidst the stunning backdrop of peaks, including Mt. Everest, if the weather allows.
    - **Late Morning:**
      - Return to Kathmandu. If not visiting Nagarkot, consider the sacred **Pashupatinath Temple** or the magnificent **Boudhanath Stupa**.
    - **Afternoon:**
      - Relax in the **Garden of Dreams**, a restored historic garden offering serenity and beauty in Kathmandu.
    - **Evening:**
      - Enjoy a final dinner with favorites like momos (dumplings), savoring the flavors of Nepali cuisine one last time. Practice saying "Mitho cha" to compliment your meal.
    - **Departure:**
      - Head to Tribhuvan International Airport for your flight, leaving Nepal with cherished memories and perhaps new friendships along the way.
    
    ### Tips:
    - Respect local customs by dressing modestly, especially when visiting religious sites.
    - Stay prepared for the weather by dressing accordingly for the season.
    - Consider using offline translation apps if needed in areas with less English proficiency.
    - Make adjustments based on your interests and flight schedule to personalize your adventure.
    
    Enjoy a journey filled with cultural insights, natural wonders, and meaningful connections in Nepal! Safe travels!
    
    TERMINATE
    [Prompt tokens: 1780, Completion tokens: 791]
    ---------- Summary ----------
    Number of messages: 5
    Finish reason: Text 'TERMINATE' mentioned
    Total prompt tokens: 3991
    Total completion tokens: 2460
    Duration: 28.00 seconds
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Plan a 3 day trip to Nepal.', type='TextMessage'), TextMessage(source='planner_agent', models_usage=RequestUsage(prompt_tokens=40, completion_tokens=712), content='Nepal is a stunning destination with its rich cultural heritage, breathtaking landscapes, and friendly people. A 3-day trip to Nepal is short, so let\'s focus on maximizing your experience with a mix of cultural, adventure, and scenic activities. Here's a suggested itinerary:\n\n### Day 1: Arrival in Kathmandu\n- **Morning:**\n  - Arrive at Tribhuvan International Airport in Kathmandu.\n  - Check into your hotel and freshen up.\n- **Late Morning:**\n  - Visit **Swayambhunath Stupa** (also known as the Monkey Temple). This ancient religious site offers a panoramic view of the Kathmandu Valley.\n- **Afternoon:**\n  - Head to **Kathmandu Durbar Square** to explore the old royal palace and various temples. Don’t miss the Kumari Ghar, which is home to the living goddess.\n  - Have lunch at a nearby local restaurant and try traditional Nepali cuisine.\n- **Evening:**\n  - Explore the vibrant streets of **Thamel**, a popular tourist district with shops, restaurants, and markets.\n  - Dinner at a cozy restaurant featuring Nepali or continental dishes.\n\n### Day 2: Day Trip to Patan and Bhaktapur\n- **Morning:**\n  - Drive to **Patan (Lalitpur)**, only a few kilometers from Kathmandu. Explore **Patan Durbar Square** with its incredible temples and ancient palaces.\n- **Late Morning:**\n  - Visit the **Patan Museum** for its unique collection of artifacts.\n  - Optional: Visit the nearby **Golden Temple (Hiranya Varna Mahavihar)**.\n- **Afternoon:**\n  - Head to **Bhaktapur**, about an hour\'s drive from Patan. Visit **Bhaktapur Durbar Square**, known for its medieval art and architecture.\n  - Try some local **"juju dhau"** (king curd) – a must-taste in Bhaktapur.\n- **Evening:**\n  - Return to Kathmandu for an evening of relaxation.\n  - Dinner at a restaurant with cultural performances, such as traditional Nepali dance.\n\n### Day 3: Nature Excursion and Departure\n- **Early Morning:**\n  - If interested in a short trek, consider a half-day hike to **Nagarkot** for sunrise views over the Himalayas. This requires an early start (leave around 4 AM). You can also enjoy a hearty breakfast with a view.\n- **Late Morning:**\n  - Return to Kathmandu. If trekking to Nagarkot isn’t feasible, visit the **Pashupatinath Temple**, a UNESCO World Heritage site, or the nearby **Boudhanath Stupa**.\n- **Afternoon:**\n  - Visit the **Garden of Dreams** for some tranquility before departure. It’s a beautifully restored, serene garden.\n- **Evening:**\n  - Depending on your flight schedule, enjoy some last-minute shopping or relishing Nepali momos (dumplings) before you head to the airport.\n- **Departure:**\n  - Transfer to Tribhuvan International Airport for your onward journey.\n\n### Tips:\n- Check the weather and prepare accordingly, especially if visiting during the monsoon or winter.\n- Respect local customs and traditions, especially when visiting religious sites. Dress modestly and be mindful of photography rules.\n- Consider adjusting this itinerary based on your arrival and departure times and personal interests.\n\nI hope you have an unforgettable experience in Nepal! Safe travels!', type='TextMessage'), TextMessage(source='local_agent', models_usage=RequestUsage(prompt_tokens=768, completion_tokens=604), content='Nepal offers a blend of natural beauty, rich culture, and historical wonders. For a condensed yet fulfilling 3-day trip, the following itinerary focuses on providing a diverse taste of what Nepal has to offer:\n\n### Day 1: Explore Kathmandu\n- **Morning:**\n  - Arrive at Tribhuvan International Airport.\n  - Check into your hotel and rest or freshen up.\n- **Late Morning:**\n  - Visit **Swayambhunath Stupa** (Monkey Temple) for panoramic views and insight into Nepalese spirituality.\n- **Afternoon:**\n  - Explore **Kathmandu Durbar Square**, where you can admire historic palaces and temples.\n  - Have lunch nearby and try traditional Nepali dishes like dal bhat (lentils and rice).\n- **Evening:**\n  - Stroll through **Thamel**, a lively district filled with shops and restaurants.\n  - Enjoy dinner at a cultural restaurant featuring a traditional Nepali dance show.\n\n### Day 2: Discover Patan and Bhaktapur\n- **Morning:**\n  - Head to **Patan** to explore **Patan Durbar Square**, known for its stunning Newar architecture.\n  - Visit the **Patan Museum** to learn about Nepalese history and art.\n  - Optional: Visit the **Golden Temple (Hiranya Varna Mahavihar)**.\n- **Afternoon:**\n  - Travel to **Bhaktapur**, a medieval town famous for its well-preserved architecture.\n  - Visit **Bhaktapur Durbar Square** and enjoy the artistic temples and palaces.\n  - Savor local specialties like **"juju dhau"** (king curd).\n- **Evening:**\n  - Return to Kathmandu for dinner and relaxation.\n\n### Day 3: Nature and Spirituality\n- **Early Morning:**\n  - Depart for **Nagarkot** to catch the sunrise over the Himalayas, offering breathtaking views of peaks including Mount Everest. If possible, enjoy breakfast with the scenic backdrop.\n- **Late Morning:**\n  - Return to Kathmandu. Alternatively, visit the **Pashupatinath Temple**, one of Nepal\'s holiest Hindu sites.\n- **Afternoon:**\n  - See the majestic **Boudhanath Stupa**, one of the largest stupas in the world.\n  - Relax in the **Garden of Dreams**, a peaceful oasis in the city.\n- **Evening:**\n  - Enjoy a final meal featuring local favorites such as momos (dumplings) before heading to the airport.\n- **Departure:**\n  - Transfer to Tribhuvan International Airport for your departure.\n\n### Tips:\n- Dress modestly and be respectful when visiting religious sites.\n- Adjust the itinerary based on your interests and flight times.\n- Consider the weather; pack appropriately for the season.\n\nThis itinerary offers a snapshot of Nepal\'s diverse attractions, blending cultural immersion with natural beauty. Wishing you a memorable trip! Safe travels!', type='TextMessage'), TextMessage(source='language_agent', models_usage=RequestUsage(prompt_tokens=1403, completion_tokens=353), content='Your 3-day trip to Nepal is well-planned, giving you a taste of the country\'s vibrant culture, rich history, and breathtaking landscapes. Here are some important language and communication tips that will enhance your experience:\n\n1. **Basic Nepali Phrases**: While English is widely spoken in tourist areas, learning a few basic Nepali phrases can be helpful and appreciated by locals. Here are some to consider:\n   - Namaste (नमस्ते) – Hello\n   - Dhanyabad (धन्यवाद) – Thank you\n   - Mitho cha (मिठो छ) – It\'s delicious\n   - Kripya (कृपया) – Please\n   - Maaph garnus (माफ गर्नुहोस्) – Sorry/Excuse me\n\n2. **Gesture Understanding**: In Nepal, the slight tilting head nod means "yes," and shaking your head left to right can mean "no." This might be different from some Western countries where nodding generally signifies agreement.\n\n3. **Respect and Etiquette**: When visiting religious sites, remove shoes and hats before entering. It\'s respectful to use your right hand when giving or receiving something, as the left hand is considered impure in Nepali culture.\n\n4. **Offline Translation Apps**: Consider downloading an offline translation app or phrasebook in case you find yourself in areas where English might not be as common.\n\n5. **Non-Verbal Communication**: A smile goes a long way in Nepal. If you encounter a language barrier, hand gestures and a friendly demeanor can be very effective.\n\nWith these tips in mind, your itinerary seems well-rounded, giving you a rich experience in Nepal. Enjoy your trip and the diverse experiences Nepal has to offer!', type='TextMessage'), TextMessage(source='travel_summary_agent', models_usage=RequestUsage(prompt_tokens=1780, completion_tokens=791), content='Here\'s your comprehensive and integrated 3-day travel plan for an unforgettable trip to Nepal. This itinerary focuses on delivering a taste of Nepal\'s culture, history, nature, and hospitality, while incorporating practical language and cultural tips to enhance your experience.\n\n### Day 1: Arrival and Cultural Exploration in Kathmandu\n- **Morning:**\n  - Arrive at Tribhuvan International Airport in Kathmandu. Begin your adventure by checking into your hotel to rest and freshen up.\n- **Late Morning:**\n  - Explore **Swayambhunath Stupa** (Monkey Temple), a symbolic and spiritual site offering magnificent panoramic views of the Kathmandu Valley. Learn basic Nepali phrases like "Namaste" to greet locals warmly.\n- **Afternoon:**\n  - Visit the historic **Kathmandu Durbar Square** to admire the old royal palace and the surrounding temples, including the Kumari Ghar, home to the living goddess.\n  - Have lunch at a nearby restaurant and try dishes like dal bhat to get a flavor of traditional Nepali cuisine.\n- **Evening:**\n  - Stroll through the vibrant streets of **Thamel**, a hub for tourists with many shops and eateries. Use simple gestures and smiles as you interact with local shopkeepers.\n  - Enjoy dinner at a restaurant with cultural performances, including traditional Nepali dance. Practice "Dhanyabad" to show appreciation.\n\n### Day 2: Discovering Heritage in Patan and Bhaktapur\n- **Morning:**\n  - Travel to **Patan** to explore the beautiful **Patan Durbar Square** and the **Patan Museum**, marveling at its rich Newar architecture and extensive collection of artifacts.\n  - Optionally, visit the nearby **Golden Temple (Hiranya Varna Mahavihar)**.\n- **Afternoon:**\n  - Head to the ancient city of **Bhaktapur**, around an hour\'s drive from Patan. Visit **Bhaktapur Durbar Square**, known for its well-preserved pagodas and temples.\n  - Relish the local specialty, **"juju dhau"** (king curd), an unmissable treat in Bhaktapur.\n  - Use polite phrases like "Kripya" (please) and "Maaph garnus" (excuse me) during interactions.\n- **Evening:**\n  - Return to Kathmandu for dinner and unwind. Embrace the gentle head nod culture when communicating to show understanding and respect.\n\n### Day 3: Embracing Nature and Spirituality\n- **Early Morning:**\n  - Venture to **Nagarkot** early to catch the breathtaking sunrise over the Himalayas. Savor a hearty breakfast amidst the stunning backdrop of peaks, including Mt. Everest, if the weather allows.\n- **Late Morning:**\n  - Return to Kathmandu. If not visiting Nagarkot, consider the sacred **Pashupatinath Temple** or the magnificent **Boudhanath Stupa**.\n- **Afternoon:**\n  - Relax in the **Garden of Dreams**, a restored historic garden offering serenity and beauty in Kathmandu.\n- **Evening:**\n  - Enjoy a final dinner with favorites like momos (dumplings), savoring the flavors of Nepali cuisine one last time. Practice saying "Mitho cha" to compliment your meal.\n- **Departure:**\n  - Head to Tribhuvan International Airport for your flight, leaving Nepal with cherished memories and perhaps new friendships along the way.\n\n### Tips:\n- Respect local customs by dressing modestly, especially when visiting religious sites.\n- Stay prepared for the weather by dressing accordingly for the season.\n- Consider using offline translation apps if needed in areas with less English proficiency.\n- Make adjustments based on your interests and flight schedule to personalize your adventure.\n\nEnjoy a journey filled with cultural insights, natural wonders, and meaningful connections in Nepal! Safe travels!\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/examples/travel-planning.ipynb)

[ __Show Source](../../../_sources/user-guide/agentchat-user-guide/examples/travel-planning.ipynb.txt)