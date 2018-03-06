# CloudSMS
Winner of the StarterHacks 2018 Mentors Choice Award - Posted for archival &amp; portfolio purposes

CloudSMS - Your Offline Web Browser

The Problem: Our world is digitally connected in the 21st century, many people have cellular plans, but still lack access to the internet through them. We believe that access to the internet should be considered a vital aspect in connecting with the world. Furthermore, a lot of people often use their data intermittently for quick searches, facts, images, or directions, this compounds and wastes data. We thought about a solution to this.

Our Solution: CloudSMS attempts to mobilize information from the web by making it accessible through other forms of communication that don't require an internet connection, specifically through text message. We allow you to obtain information about people, places, things, weather, directions, categorized news, as well as images and more, by simply sending a text message to a number. This allows you to obtain valuable information in times where you don’t have data. For example, this can be specifically useful in northern aboriginal communities where data connectivity is an issue. CloudSMS can be employed in cases like these to bridge this digital gap. Furthermore, this can be used if you would simply like to conserve your data.

The Future: We hope to consolidate this project as a more robust search engine that you can use, we hope to use our own algorithms and optimizations to make these messages exchangeable as fast as possible. We hope to soon implement a method in which the service could obtain your location to use as an aid when answering your questions.

Monetization: We intended for this project to be a nonprofit, but changes could be made to monetize the platform. For example, adsense can be employed in the same way that Google does it with their organic search engine. When searching for locations, restaurants, or shops within our platform, ones that are sponsored can be displayed with priority. This, and many more applications allow this platform to be flexible and powerful in delivering the experience that a business desires.

Try out CloudSMS right now, by texting an query to (226) 242-9729 in the form of a question or command, text "EXAMPLES" to the number to view some examples to get started. NOTE: MMS Must be enabled to get images/map images

CloudSMS connects you when you would otherwise not be connected.

Running:
Install Flask, Pillow, twilio's API, newsapi's client, google api's client, and make sure you are able to accept external connections to the web server that is started (by default on port 44) by the program. Then, set your twilio webhooks to point to the web server after it is running and listening on the proper port. The DEBUG version is meant to be used only if you want to view all outputs, and may be a little bit buggy.
