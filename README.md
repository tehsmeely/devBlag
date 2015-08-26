#DevBlag
A Blog using Django and Djangae on Google app engine,
build to specialise in blogging about software/game development


##Feature Wishlist

* code blocks with syntax highlighting
* Markdown in posts, such as adding links
* Linkable screenshots with previews
* source downloads support.

##Djangae
This is made using Potato's Djangae and based off of [djangae scaffold](https://github.com/potatolondon/djangae-scaffold)

##GAE hosting
This is hosted currently [here](https://dark-foundry-91520.appspot.com/), though it's not finished and optimised for this platform yet.

##The Resource system
A resource being anything other than the raw text of post, so thats pictures, files to download, and code snippets. These are kept independent of posts, while a user may upload and link directly into a post, these are also viewable externaly, and used later without re-upload. They can also exist purely non-rerlated to a post, such as the icon for a project or a developer.

##Developer users
Developers are elevated users.
Normal users can apply to become developers, who can then post into projects and create their own

##Projects
An individual project being worked on by one or more developers, posts are entered under these as topics.


##Post Markup
Resources are added to post bodies and inserted via a custom regex markup.
Resources are tagged as <<[type]:[resource id]>>, though users may see this, they dont have to add it as this is inserted by clicking a table at the bottom of the post adding page

Links can be added to posts by using the standard markdown style: \[text\]\(url\)