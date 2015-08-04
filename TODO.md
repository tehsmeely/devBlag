#TODO




Add Logging *-This is special cos GAE* 

~~ResID is redundant~~ *-removed*

Decomm associatedProject on resources
Decomm resource_mappings


Migrate views to class-based
*-Still not sure if i want to do this*


developer_required view funct wrapper
*- i believe this is sorted ... it's been a week*


Post management.
Creation vs Publishing to enable editing before release to the world at large
*-Post specific page? AddPost can redirect here on success then*
	*-Done, pretty much!*

Resource management.
Developers can see, manage, [and delete]? their resources
*-mostly done. can see and delete resources on profile page*

Post Entry *-pretty much sorted*
Project Creation **
User Creation *-automatic, i dont need to worry about that!*

User -> Developer upgrading *-a link on the profile page*

~~Post Comments~~ *-Too much for this*


Ideas:

Post tags
    *-added in a basic format, might be improved upon*
~~User chosen post background colours - need a non-intrusive way of picking~~
	~~perhaps a dropdown list of a limited set of presets~~
	*-Added, a very sexy JS colourpicker*

~~CSRF~~ *-sorted*

Enhance current "handle body" which is basically markup
	~~add support for named links in posts~~



On LIVE:

    Move all style and script to external files for CSP raisins
    See about getting a version of JQueryUI with just the used widgets 