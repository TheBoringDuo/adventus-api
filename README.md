![logo](https://raw.githubusercontent.com/TheBoringDuo/adventus-web/main/drawables/adventus.svg "Adventus Logo")
# Adventus API (Back End)
This repo contains the source code and documentation of the back end API of Adventus. 

## Usage
The API is hosted on the following URL:
<pre>https://adventus-api.ml/</pre>

Every API call is simply appended to the end of the server's URL and the returned results are always in JSON format. Here is a list of officially supported API commands:
-     findhotels/*countryName*/*cityName*/*keywords*/
  Finds hotels for a selected destination and returns them sorted by relevance. The parameter *keywords* is optional and when omitted the returned objects are sorted by overall rating. In case your app doesn't have separate fields for city and country, you can pass "customsearch" as a *countryName* parameter.
  <p style="margin-bottom: 2em;"></p>
-     findrestaurants/*countryName*/*cityName*/*keywords*/
  Finds restaurants for a selected destionation and [optionally] with given keywords. Works the same way as "findhotels/"
  <p style="margin-bottom: 2em;"></p>
-     register/
  Creates a new user account with given *email*, *password*, *first_name* and *last_name* as POST parameters. Returns back the email, first_name and last_name.
  <p style="margin-bottom: 2em;"></p>
-     api/token/
  Signs into a user account with given *email* and *password*, as POST parameters. Returns back two strings called *access* and *refresh* respectively. The first one is a JWT Access Token (valid for 7 days) that every user-specific API call requires as authorization. The second one is the refresh token which remains unused for now.
  <p style="margin-bottom: 2em;"></p>
-     api/password_reset/
  Requests a password reset for a given *email* as a POST parameter. The user will receive a password reset link in their inbox.
  <p style="margin-bottom: 2em;"></p>
-     profile/
  [Requires JWT Authorization] Provides basic information about the user: *first_name*, *last_name*, *email*, *date_joined*, and *id*.
  <p style="margin-bottom: 2em;"></p>
-     add_to_favourites/
  [Requires JWT Authorization] Adds an object to favorites by given *obj_id* as a POST parameter.
  <p style="margin-bottom: 2em;"></p>
-     remove_from_favourites/
  [Requires JWT Authorization] Removes an object from favorites by given *obj_id* as a POST parameter.
  <p style="margin-bottom: 2em;"></p>
-     favourite_hotels/
  [Requires JWT Authorization] Returns a list of hotels that the user has added to their favorites.
  <p style="margin-bottom: 2em;"></p>
...and we have more to come! Stay tuned.
