# revision system:

## goals:
* every time a user updates a page, a revision is created to save that version (and who created it)
* it should be cheap to see the current version of the page
* it should be possible to revert to a previous version of the page

* Alice creates a page (the original page, version 0)
* Bob edits the page (version 1)
* Charlie edits the page (version 2)
* Dar edits the page (the current page, version 3)

the history detail headers / content should look like this:

current (2022-03-12) | Dar | version 3
    * 1234
2022-03-11 | Charlie | version 2
    * 123
2022-03-10 | Bob | version 1
    * 12
2022-03-09 | Alice | version 0
    * 1

a user decides to revert to version 1, Bob's version, and the detail headers now looks like:
current (2022-03-10) | Bob
2022-03-09 | Alice

where is the information for all of this stored?

for convinience, optimization, and what honestly makes the most sense, the page object at any moment contains the *most recent informaiton* about a page. naively in the first example I want the page object to be
    * created by: Dar
    * created date: 2022-03-12
    * content: 1234

however I'll save myself the trouble of proceeding with this, because I won't be able to store the created date

because there is one original and 3 updates there are 3 created revisions

revision 0 (which corresponds to version 0)
    * created by: Alice
    * created date: 2022-03-09
    * content: go from "12" to "1"
revision 1 (corresponds to version 1)
    * created by: Bob
    * created date: 2022-03-10
    * content: go from "123" to "12"
revision 2 (corresponds to version 2)
    * created by: Charlie
    * created date: 2022-03-11
    * content: go from "1234" to "123"
page (corresponds to version 3)
    * created by: dar
    * created date: 2022-3-12
    * content: "1234"

## summary
* each revision contains the information to go from the current version to the previous version
* each revision contains the date the previous version was created
    * _not_ the date the revision was created, that's stored in the page
* each revision contains the user who the previous version is created by
