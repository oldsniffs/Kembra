[33mcommit 9b33f95043801137dc94ed58d95c2438ed1e7bcd[m[33m ([m[1;36mHEAD -> [m[1;32mmaster[m[33m, [m[1;31morigin/action[m[33m, [m[1;32maction[m[33m)[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Tue Aug 13 14:40:08 2019 -0400

    Reorganized Command / Action processing. ActionCommand is now the data holding class and has execute function which calls a function name matched to the ActionCommand.verb attribute. Necessitated by this, also implemented broadcasting queues, tracked by the readable list in select.

[33mcommit efa1e2b8205c76d880434ee41d14ea7201b9bb72[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Wed Aug 7 15:39:01 2019 -0400

    removed temp open office file

[33mcommit 849a275f783215d314c11079f8f358dfedd58606[m[33m ([m[1;31morigin/master[m[33m)[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Wed Aug 7 15:36:41 2019 -0400

    ready to fork

[33mcommit eee8e15108807a547eda0e413ed9e216e5b58c08[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Tue Aug 6 14:29:35 2019 -0400

    Changed Person class name

[33mcommit d576ea4c26fb1c82bbb337ea16fbb9d3c963ac88[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Mon Aug 5 12:29:39 2019 -0400

    Moving problem fixed, now working properly

[33mcommit 31bc4963a16a08df0566bd044b6c1dc88cf577ae[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Mon Aug 5 12:26:43 2019 -0400

    Moving problem fixed, now working properly

[33mcommit dfc884d6179f4655ec06f0d75b5def7f8bd74bd8[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sun Aug 4 16:04:33 2019 -0400

    Moving leaves a copy of yourself in denizens. people.move does not seem to be successfully removing the player from the location.denizens list as player leaves.

[33mcommit 38476b0d3baded568060af49c9021770e9389ea2[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sat Aug 3 13:35:08 2019 -0400

    Look now finds any present objects and correctly returns matched item description

[33mcommit 10283c83e6f2a16bd9194c8e8c545232b7035665[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sat Aug 3 12:07:01 2019 -0400

    Location describe() fixed:
    Solved "None in denizens" mystery. Observer=None attribute was culprit.

[33mcommit da614822a009dd00479791f1c58459d0b1483f53[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Fri Aug 2 16:24:13 2019 -0400

    Basic 'get' action handling.

[33mcommit a3c48188752441ae1f1ce687834ed8c9b52cae48[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Mon Jul 29 11:42:52 2019 -0400

    denizen description was bugging. When iterating through an empty list for location.describe, None was being found in the empty list and an error that None type has no name attribute (because names are being added to the description) was returned.
    
    Added a denizen is not None check before adding names.
    
    This is an unsatisfying solution because I don't understand why the problem arose. I checked the lists after world creation and there was no None element in the list. It was empty.

[33mcommit 1c4348310854a7fa6165955080d19be00f8c14bb[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sun Jul 28 14:11:53 2019 -0400

    Added advanced formatting to display_text_output

[33mcommit d707cccd74fe5aa1e253aed0eea02e24e5b44395[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sun Jul 28 11:54:12 2019 -0400

    added network.py

[33mcommit 63aea272e79cff7a2c1a45b61f660888f32a238d[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sun Jul 28 11:42:39 2019 -0400

    Reorganized location description algorithm

[33mcommit 3796fdbb1e3f54f955e75526ec7293ee1b98a65c[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sun Jul 28 09:05:02 2019 -0400

    Fixed newline > color issue at end of client.display_text_output

[33mcommit 2839409f49d701b4e7c72185d62f058304d0d68c[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sat Jul 27 16:18:31 2019 -0400

    talking

[33mcommit 05ac13864487cafb6a999b573156a3059ff77c59[m
Author: Thomas Austin <austin.thomas@protonmail.com>
Date:   Sat Jul 27 12:09:51 2019 -0400

    base ready
