# How To's
This Project consists of a collection of Web Applications that allow you to manage, edit and view How To's in the form of Step-By-Step procedures. An important key aspect is the modularity of the documentation. Reusable steps, pictures, explanations, links are a core concept and the database is designed with that in mind.

### [Core API](https://github.com/tiveritz/how-tos-api)
The REST API that handles all database interactions on the documentation database.<br>

### [Webapps](https://github.com/tiveritz/how-tos-webapps)
Webapplications that allow content management and a viewer for the users. Consume the Core API.

# Core API
* RESTful witch JSON payload
* HTTPS over SSL
* API versioning preparation
* Beautiful URLs
* Authentication
* Ensured data integrity
<br/>

| BASE                     | URL                  | GET   | POST  | PUT   | PATCH | DELETE |
| ------------------------ | -------------------- | :---: | :---: | :---: | :---: | :----: |
| api.tiveritz.at/hwts/v1/ | howtos               |   ✓   |   ✓   |       |       |        |
| api.tiveritz.at/hwts/v1/ | howtos/{id}          |   ✓   |       |       |   ✓   |   ✓    |
| api.tiveritz.at/hwts/v1/ | howtos/{id}/linkable |   ✓   |       |       |       |        |
| api.tiveritz.at/hwts/v1/ | howtos/{id}/steps    |       |   ✓   |       |   ✓   |   ✓    |
| api.tiveritz.at/hwts/v1/ | statistics           |   ✓   |       |       |       |        |
| api.tiveritz.at/hwts/v1/ | steps                |   ✓   |   ✓   |       |       |        |
| api.tiveritz.at/hwts/v1/ | steps/{id}           |   ✓   |       |       |   ✓   |   ✓    |
| api.tiveritz.at/hwts/v1/ | steps/{id}/linkable  |   ✓   |       |       |       |        |
| api.tiveritz.at/hwts/v1/ | steps/{id}/steps     |       |   ✓   |       |   ✓   |   ✓    |
<br/>

#### GET howtos
Get a list of all How To's with relevant list data, sorted by last change descending<br/>
#### POST howtos
Create a new How To. A title can be posted but is not mandatory<br/>
#### GET howtos/{id}
Get a specific How To including the Steps as tree<br/>
#### PATCH howtos/{id}
Change a specific How To<br/>
#### DELETE howtos/{id}
Deletes a specific How To. Data integrity is ensured and all connected entries are also deleted (URI IDs, Steps)<br/>
The client is responsible to warn about cascade deletion.<br/>
#### GET howtos/{id}/linkable
Get a list of all Steps that can be added to the How To<br/>
#### POST howtos/{id}/steps
Add a Step to a How To<br/>
#### PATCH howtos/{id}/steps
Change Step order<br/>
#### DELETE howtos/{id}/steps
Remove a linked Step from a How To<br/>
<br/>

#### GET statistics
Statistical data about the available content<br/>
<br/>

#### GET steps
Get a list of all Steps with relevant list data, sorted by last change descending<br/>
Supersteps are marked (isSuper), to allow the client to mark them<br/>
#### POST steps
Create a new Step. A title can be posted but is not mandatory<br/>
#### GET steps/{id}
Get a specific Step including the Substeps as tree<br/>
Supersteps are marked (isSuper), to allow the client to mark them<br/>
#### PATCH steps/{id}
Change a specific Step<br/>
#### DELETE steps/{id}
Deletes a specific Step. Data integrity is ensured and all connected entries are also deleted (URI IDs, Super connections, Sub connections)<br/>
The client is responsible to warn about cascade deletion.<br/>
#### GET steps/{id}/linkable
Get a list of all Substeps that can be added to the Step<br/>
#### POST steps/{id}/steps
Add a Step to another Step (add Substep to Superstep)<br/>
#### PATCH steps/{id}/steps
Change Substep order<br/>
#### DELETE steps/{id}/steps
Remove a Step from another Step (remove Substep from Superstep<br/>
<br/>

## Web Applications Diagram
![](./docs/server.png?raw=true "How To's server diagram")

## UML
![](./docs/uml.png?raw=true "How To's UML")


## Core Features
Depending on the complexity and time of the project various features can be implemented. Sorted by priority descending.
* How To's include steps, sortable
* Steps used as Supersteps (wich linked Substeps) or Steps (with explanations), sortable
* Steps and Supersteps reusable (used by various Supersteps / How To's)
* How To's, Supersteps, Substeps have content (title, description, notes, to do's), depending on what makes sense
* Steps have Explanations
* API reference not by Database id but specific string or number (beautify URLs)
* Explanations have content (title, description, note, to do's)
* Explanations contain Explanation Modules
* Explanation Module Text
* Explanation Module Code
* Explanation Module Text contain links
* Explanation Module Text contain pictures (Depending on the Editor Framework -> research required
* Link can be external or internal
* Internal / External links can be managed
* Module Knowledge Base
* Module Knowledge Base contains Explanations


## Requirements
pip install cryptography==3.4.7
pip install Django==3.2.4
pip install django-filter==2.4.0
pip install djangorestframework==3.12.4
pip install mysqlclient==2.0.3
pip install python-dotenv==0.18.0
