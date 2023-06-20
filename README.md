Hello! And thank you for your attention to my project. The name "hades" is a name left over from the prototype stage and does not play a significant role.

This application, written in Python using the Django framework, is a pet project of a junior developer, created to show my abilities, potential and experience. Keep in mind that the project is still a work in progress and the moment when it will be perfect enough to be considered complete has not yet been determined.

The application is a blog site for creating articles on the subject of video games. Although a potential user has the opportunity to write articles on neutral topics.
A demo, non-commercial version is available on Dockerhub at the link below:

Describing the project, I would like to highlight its three main parts:
1) The ability to share privileges between users, giving them the roles of moderators or administrators, when by default, immediately after registration, the user will not have these capabilities. This is determined by the administrator through the appropriate panel;
2) Ability to follow users and be tracked by them. Followers feature;
3) The most important thing is the possibility of creating your own blog as such. The user can manage his feed, supplementing everything with new and new articles, using a fairly flexible and tool-rich editor.

Analyzing the first point, I want to note such features of the application as full CRUD of sections related to the site's subject matter - games, developers, genres. A user with moderator privileges does not have access to the Django administrative panel, but has the ability to make changes to existing data in the sections listed above, as well as create new ones. Of course, the data of these sections are logically connected to each other in Django models, respectively, in the database.

Analyzing the second point, the possibility of using which is available to all users, I will note the possibility of creating two lists, the first of which will indicate the users who are subscribed to the authorized user, and the second will list everyone whom the authorized user follows.


Analyzing the third point, the possibility of using which is also available to all registered users and which is the basis of the entire project, I will note a rather simple, but quite rich in tools for creativity editor. (I used Froala WYSWIG).

The application has checks for errors, where possible, and checks for intentional injections of malicious code.

The work on the project is still ongoing, and the README will be supplemented and become more detailed.

Thank you very much for your attention and time.

Mail at which you can write me a letter:

sytnikserhii22038@gmail.com
