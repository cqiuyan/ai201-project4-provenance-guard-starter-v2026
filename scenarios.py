"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Ten paragraphs from two of my own essays: a fellowship essay and a
        # documentary reflection. The essays split into eleven paragraphs; the
        # shortest (38 words, on stromatolites) is left out to make ten.
        "texts": [
            'Growing up in a small rural village in China, I never imagined how far my journey would take me. When I was seven, my grandmother told me that my sisters and I were moving to America in search of the “American Dream.” My mother, raising six daughters in a culture that valued sons, wanted to create new opportunities for us. Leaving was difficult, but adapting to American life opened my eyes to new cultures and possibilities.',
            'On my first day of school in America, I couldn’t understand a single word my teacher said, but I wrote down every note, determined to keep up. Each day, I understood a little more. Today, I can write pages of essays and even research papers. The journey taught me that change, though daunting, can be transformative. Just as a rocket must face resistance before reaching orbit, every challenge can become a source of strength.',
            'I was inspired by Amanda Nguyen, who paused her astronaut career to help found the Sexual Assault Survivors’ Bill of Rights based on her experience, changing laws in the U.S. and in the United Nations. She later continued her dream of spaceflight with the Blue Origin launch in 2025. Her journey showed me that the path to victory is not easy, but dedicated commitment can persist. Like her, I have learned to turn hardship into momentum. I turn disapproving voices into fuel for self-improvement. When people mocked me with words like “ching chong” or doubted that I could become an engineer, I worked even harder.',
            'As a first-generation college student, I continue my education to keep growing and learning. I am grateful for the people and communities that helped me get here, like Girls Who Code and the Break Through Tech program. The mentorship I received inspired me to give back as a mentor. I want to tell another girl to dream big and know she is good enough. As a Peer Believe Mentor, I support underclassmen navigating university life, especially first-generation and limited-income students who feel out of orbit. We brainstorm activities like building bridges from pasta and free Chick-fil-A dinners to foster community bonding. Through these experiences, I’ve learned that leadership isn’t just about leading, but also listening, guiding, and creating spaces where others feel they belong.',
            'Technology is not just about machines, it empowers people, connects communities, and pushes boundaries across distances. Innovation should serve humanity, not replace people, but help them accomplish their goals more efficiently. My team built a fitness-tracking app during a hackathon that analyzed workout data to help users adjust their routines, not to replace coaches, but to better understand their habits. The process wasn’t easy with time constraints and the use of new tools like Swift, but we persisted step by step until every button worked. The experience showed me that collaboration and perseverance can bring ideas to life. I hope to use my technology skills to contribute to the galaxy as one of the bright stars.',
            'At this stage in my journey, I’m ready for a greater mission: to unite my passion for technology, equality, and exploration. I aspire to work at the intersection of AI and aerospace innovation, developing intelligent systems that make space travel safer, more sustainable, and more inclusive. The Brooke Owens Fellowship represents the next step in that mission.',
            'From my grandmother’s village to WashU and onward to my future career, each challenge has been a launch and each opportunity a new orbit. The little rural village girl went to the city to do big things—going to college, earning her degree, and chasing her dreams.',
            "I think How the Earth Was Made is a good documentary because it connects what I already knew to new knowledge, especially fun facts about places I have visited before. One interesting example was how Kelvin estimated Earth's age by treating it as a cooling rock. It shows how science has improved over time, from early estimates to the accepted age of 4.5 billion years. I also never really thought about where Earth's water originally came from. In my mind, water has always been here, constantly recycled between phases of gas, liquid, and solid.",
            "Another part I found interesting was how plate tectonics created landscapes we see today. For example, the Matterhorn formed from the collision of the African and European plates, and its peak is a part of the African continent but lay on top of Europe. I didn't know this when I visited the Matterhorn while studying abroad, which made this fact especially surprising. I stared at it and thought of the chocolate toblerone.",
            "The video made me think about how Earth has gone through so many different phases, from extreme volcanic activity to ice ages. With global warming being such a big topic today, I wonder what Earth's climate will look like in the distant future when the Earth goes through a constant change of phases of weather. Humans are so small in comparison to Earth's existence and how dinosaurs made up one-third of Earth’s living organism history, but we have only been around for so long.",
        ],
    },
    {
        "name": "plain writing",
        "criterion": 2,
        # Plainly written human passages from the unit 8 attack set's
        # false-positive family: short sentences, common words.
        "texts": [
            # FP01: plain, clear writing with no flourishes
            'We got to the campsite about four. The pitch was fine, a bit sloped, but there was a tap nearby and the toilets were clean enough. Putting the tent up took longer than it should have because I had forgotten how the poles went. The weather held until Saturday night. Then it rained hard and kept raining. We stayed in the tent and played cards and ate most of the food we had brought for Sunday. On Sunday we packed up wet and drove home early. It was not the weekend we planned but the kids enjoyed it and we would go back.',
            # FP03: a non-native English speaker writing carefully
            'I want to describe my experience of the first month in this country. The weather was very different from my home. I did not expect the rain to continue for so many days. My colleagues were kind and they helped me to find an apartment. I am still learning the words that people use in the office. Sometimes I do not understand the jokes. But I am happy that I came here and I think it was a good decision for my family.',
            # FP04: a student essay written to a rubric
            'There are three main causes of the conflict. The first cause is economic. Trade between the two regions had declined significantly in the preceding decade. The second cause is political. Neither government was able to control its own border provinces effectively. The third cause is social. Population movements had created communities on both sides with divided loyalties. In conclusion, the conflict cannot be explained by any single factor.',
            # FP05: technical documentation written by a person
            'To configure the service, edit the settings file in the installation directory. Set the host value to the address the service should bind to. Set the port value to an unused port above 1024. Save the file and restart the service. The service will log its startup configuration. If the port is already in use, the service will exit with an error. Check the log file for details before retrying.',
            # FP07: a phrase repeated on purpose
            'It rained on Monday. It rained on Tuesday. It rained on Wednesday and it rained on Thursday and by Friday I had stopped looking out of the window altogether. The forecast said it would clear. The forecast said that on Monday, and on Tuesday, and on Wednesday. I have stopped believing the forecast. I have started believing the window.',
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # Three I'm confident are AI, three I'm confident are human, three
        # borderline. Each label has to come up at least once per trial.
        "texts": [
            # AI: generated corporate boilerplate
            "In today's fast-paced digital landscape, effective communication is more important than ever. By leveraging innovative tools and fostering a culture of collaboration, organizations can unlock new opportunities for growth. Ultimately, success depends on a commitment to continuous improvement and adaptability.",
            # AI: generated essay on remote work
            'Remote work has fundamentally transformed the way organizations operate. It offers employees greater flexibility and eliminates lengthy commutes. Additionally, it allows companies to access a broader talent pool. However, remote work also presents several challenges. Communication can become more difficult without face-to-face interaction. Furthermore, maintaining team cohesion requires intentional effort. Overall, the success of remote work depends on clear policies, effective tools, and a strong organizational culture.',
            # AI: generated essay on time management
            'Time management is an essential skill for students and professionals alike. By prioritizing tasks and setting clear goals, individuals can make the most of their available time. Additionally, breaking large projects into smaller steps helps reduce stress and improve focus. It is also important to schedule regular breaks to maintain productivity. Ultimately, effective time management leads to better outcomes and a healthier work-life balance.',
            # human: Federalist No. 10 opening (1787)
            'Among the numerous advantages promised by a well-constructed Union, none deserves to be more accurately developed than its tendency to break and control the violence of faction. The friend of popular governments never finds himself so much alarmed for their character and fate, as when he contemplates their propensity to this dangerous vice. He will not fail, therefore, to set a due value on any plan which, without violating the principles to which he is attached, provides a proper cure for it. The instability, injustice, and confusion introduced into the public councils, have, in truth, been the mortal diseases under which popular governments have everywhere perished; as they continue to be the favorite and fruitful topics from which the adversaries to liberty derive their most specious declamations.',
            # human: attack set FP02, a formal report
            'This report sets out the findings of the working group. The group met four times between January and March. Its remit was to review the current arrangements and to recommend changes where these were warranted. The group found that the existing arrangements are broadly sound. Three areas were identified where improvement is possible. These are set out in section four, together with an indicative timetable. The group recommends that the committee adopt the proposals in full.',
            # human: attack set FP06, a person following a cover-letter template
            'Dear Sir or Madam, I am writing to enquire about the position advertised on your website. I have five years of relevant experience and I believe I would be a strong fit for the role. I have attached my curriculum vitae for your consideration. I am available for interview at your convenience. Thank you for your time. I look forward to hearing from you.',
            # borderline: the remote-work essay, lightly edited by hand
            "Remote work has changed how a lot of companies operate. It gives people more flexibility and gets rid of long commutes - which honestly is huge. It also lets companies hire from a much bigger pool. But it isn't all good. Communication gets harder without face-to-face time. And keeping a team feeling like a team takes real effort. In the end, whether remote work works comes down to clear policies, decent tools, and a culture people actually buy into.",
            # borderline: attack set EV05, AI text after a heavy human edit
            'Communication at work matters more than people say it does — and I mean the boring kind, not the away-day kind. Teams that actually tell each other things get more done. Obviously. A few things help. Regular check-ins, which everyone hates and everyone needs. Writing decisions down, so nobody has to remember what was agreed in a corridor in March. And making it genuinely safe to ask a stupid question, which is the hardest one and the one that matters most.',
            # borderline: attack set EV01, AI text with typos added
            'The importance of effective communication in the workplace cannot be overstated. Teams that communicate clearly are better poistioned to achieve their objectives and avoid costly misunderstandings. Three are several strategies organisations can adopt to improve thsi. First, establishing regular check-ins ensures that information flows cosnistently between team members. Second, documenting decisions provides a reefrence point that reduces ambiguity. Finally, encouraging an environment whree questions are welcomed helps surface issues early. Implementing thsee approaches can lead to meaningful improvements in team pefrormance and overall satisfaction.',
        ],
    },
    {
        "name": "bad input",
        "criterion": 4,
        # The six malformed requests named in criterion 4, sent as written.
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},          # no text field at all
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": 42, "creator_id": "eval_bad_number"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
        ],
        # The sixth case in criterion 4, a body that's a JSON list instead of
        # an object, can't be sent from here: run_eval.py only sends dicts.
        # I test it by hand with curl (attack RQ07 sends the same thing).
    },
    # Criterion 5 (the appeal path) is tested by hand with curl, as
    # criteria.md says: submit, take the content_id, appeal, read the log.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
