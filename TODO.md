#TODO


~~Post ordering doesnt currently work - needs fixing~~ *-done*


Add Logging *-This is special cos GAE* 

~~ResID is redundant~~ *-removed*

~~Decomm associatedProject on resources~~
~~Decomm resource_mappings~~
*-gone!*

Migrate views to class-based
*-Still not sure if i want to do this - update: no, though maybe from scratch in future!*


~~developer_required view funct wrapper~~
*- i believe this is sorted ...*


Post management.
~~Creation vs Publishing to enable editing before release to the world at large~~
*-Post specific page? AddPost can redirect here on success then*
	*-Done, pretty much!*

Resource management.
~~Developers can see, manage, [and delete]? their resources~~
*-mostly done. can see and delete resources on profile page*

~~Post Entry~~ *-pretty much sorted*

~~Project Creation~~ *-exists*

~~User Creation~ *-automatic, i dont need to worry about that!*

~~User -> Developer upgrading~~ *-a link on the profile page*

~~Post Comments~~ *-Too much for this ... feature creep?*


Ideas:

~~Post tags~~
    *-added in a basic format, might be improved upon*
~~User chosen post background colours - need a non-intrusive way of picking~~
	~~perhaps a dropdown list of a limited set of presets~~
	*-Added, a very sexy JS colourpicker*

~~CSRF~~ *-sorted*

Enhance current "handle body" which is basically markup
	~~add support for named links in posts~~ *-working nicely*



On LIVE:

    1 . ~~Move all style and script to external files for CSP raisins~~
    See about getting a version of JQueryUI with just the used widgets 



Migration:

| Template Name               | Style | Script |
| --------------------------: |:-----:|:------:|
| addPost                     |   Y   |   Y    |
| -addPost_notDev             |   N   |   N    |
| -addPostTest                |   N   |   N    |
| addResource                 |   Y   |   Y    |
| -addResource_standalone     |   N   |   N    |
| base                        |   Y   |   Y    |
| createDeveloper             |   Y   |   Y    |
| developerProfile            |   Y   |   Y    |
| index                       |   Y   |   Y    |
| notFound                    |   Y   |   Y    |
| post                        |   Y   |   Y    |
| profile                     |   Y   |   Y    |
| projectPosts                |   Y   |   Y    |