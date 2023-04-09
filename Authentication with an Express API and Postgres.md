# Authentication with an Express API and Postgres

## Setting Up

Let's make sure our Express app has the required base modules:

```bash
# within root of API
npm install --save express pg knex bcrypt
npm install --save-dev nodemon
```

Part of our `package.json` file will look like this:

```js
  "main": "server.js",
  "scripts": {
    "start": "nodemon server.js"
  }
```

### Create Users Table with Knex

[Set up `knex`](http://backend.turing.io/module4/lessons/sql-in-node) and make sure your `knexfile.js` looks like this:

```js
module.exports = {
  development: {
    client: 'pg',
    connection:'postgres://localhost/secrets',
    migrations: {
      directory: './db/migrations'
    },
    seeds: {
      directory: './db/seeds/dev'
    },
    useNullAsDefault: true
  },

  test: {
    client: 'pg',
    connection:'postgres://localhost/secrets_test',
    migrations: {
      directory: './db/migrations'
    },
    seeds: {
      directory: './db/seeds/test'
    },
    useNullAsDefault: true
  },

  production: {
    client: 'pg',
    connection: process.env.DATABASE_URL,
    migrations: {
      directory: './db/migrations'
    },
    seeds: {
      directory: './db/seeds/production'
    },
    useNullAsDefault: true
  }
};
```

We'll want to create a `users` table within our database that has the fields of `username`, `token` and `password_digest`.

```bash
knex migrate:make create-users-table
```

Hop into the migration file generated and edit to look like so:

```js
exports.up = function(knex, Promise) {
  let createQuery = `CREATE TABLE users(
    id SERIAL PRIMARY KEY NOT NULL,
    username TEXT,
    token TEXT,
    password_digest TEXT,
    created_at TIMESTAMP
  )`;
  return knex.raw(createQuery);
};

exports.down = function(knex, Promise) {
  let dropQuery = `DROP TABLE users`;
  return knex.raw(dropQuery);
};
```

```bash
knex migrate:latest
```

### User Model

When a user of your application signs up or signs in, your client application will be sending plain text to your API containing their username and password.

#### On Sign Up and Sign In User Flow

On sign up, your user will send over their username and password.

[Bcrypt](https://www.npmjs.com/package/bcrypt) will be responsible for taking that plain text password, and salting and hashing it to be stored securely in your database.

Whenever that user goes to login again, your User model will use the plain text password passed in again to compare against the salted & hashed version of it saved to your database.

If the passwords match, we'll use the built-in Node module, [Crypto](https://nodejs.org/api/crypto.html#crypto_crypto) to generate a random, secure token to store on the user's row in the database.

This token will be passed between client and server to continue reidentifying the logged-in user client-side.

## Implementing Server-Side

By now, we should have a users table in our project's database that's ready to go.

Let's quickly create a User model to house our authentication functions.

```bash
touch app/models/user.js
```

We next need to create a route to POST to `signup`.

```js
// server.js
const User = require('./models/user.js')

...

app.post('/signup', User.signup)
```

Let's make sure our User model is requiring the files necessary:

```js
const environment     = process.env.NODE_ENV || 'development';    // set environment
const configuration   = require('../../knexfile')[environment];   // pull in correct db with env configs
const database        = require('knex')(configuration);           // define database based on above
const bcrypt          = require('bcrypt')                         // bcrypt will encrypt passwords to be saved in db
const crypto          = require('crypto')                         // built-in encryption node module
```

Our `signup` function will have this flow to it:

```js
// app/models/user.js
const signup = (request, response) => {
  // get user from request body
  // encrypt plain text password with bcrypt
  // set user's password_digest to encrypted pw
  // create token to be sent back to client to create "session"
  // set user's token to created token
  // save user with password_digest and session token to database
  // respond with 201 and json of created user info
}
```

Let's dream-drive that pseudo-code to look something like this:

```js
// app/models/user.js
const signup = (request, response) => {
  const user = request.body
  hashPassword(user.password)
    .then((hashedPassword) => {
      delete user.password
      user.password_digest = hashedPassword
    })
    .then(() => createToken())
    .then(token => user.token = token)
    .then(() => createUser(user))
    .then(user => {
      delete user.password_digest
      response.status(201).json({ user })
    })
    .catch((err) => console.error(err))
}

// don't forget to export!
module.exports = {
  signup,
}
```

Now for defining those dreamed up helper functions:

```js
// app/models/user.js
// check out bcrypt's docs for more info on their hashing function
const hashPassword = (password) => {
  return new Promise((resolve, reject) =>
    bcrypt.hash(password, 10, (err, hash) => {
      err ? reject(err) : resolve(hash)
    })
  )
}

// user will be saved to db - we're explicitly asking postgres to return back helpful info from the row created
const createUser = (user) => {
  return database.raw(
    "INSERT INTO users (username, password_digest, token, created_at) VALUES (?, ?, ?, ?) RETURNING id, username, created_at, token",
    [user.username, user.password_digest, user.token, new Date()]
  )
  .then((data) => data.rows[0])
}

// crypto ships with node - we're leveraging it to create a random, secure token
const createToken = () => {
  return new Promise((resolve, reject) => {
    crypto.randomBytes(16, (err, data) => {
      err ? reject(err) : resolve(data.toString('base64'))
    })
  })
}
```

You can verify this is working for you with Postman or curl (within Terminal):

```curl
curl "http://localhost:3000/signup" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "username": "new_username",
    "password": "supersecurepassword"
  }'
```

### Sign In

We'll need a route within `server.js` to handle this request:

```js
// server.js
app.post('/signin', User.signin)
```

Let's dream-drive `/signin` as well:

```js
// app/models/user.js
const signin = (request, response) => {
  // get user creds from request body
  // find user based on username in request
  // check user's password_digest against pw from request
  // if match, create and save a new token for user
  // send back json to client with token and user info
}
```

To implement, that would look something like this:

```js
// app/models/user.js
const signin = (request, response) => {
  const userReq = request.body
  let user

  findUser(userReq)
    .then(foundUser => {
      user = foundUser
      return checkPassword(userReq.password, foundUser)
    })
    .then((res) => createToken())
    .then(token => updateUserToken(token, user))
    .then(() => {
      delete user.password_digest
      response.status(200).json(user)
    })
    .catch((err) => console.error(err))
}
```

And for our helper functions:

```js
// app/models/user.js
const findUser = (userReq) => {
  return database.raw("SELECT * FROM users WHERE username = ?", [userReq.username])
    .then((data) => data.rows[0])
}

const checkPassword = (reqPassword, foundUser) => {
  return new Promise((resolve, reject) =>
    bcrypt.compare(reqPassword, foundUser.password_digest, (err, response) => {
        if (err) {
          reject(err)
        }
        else if (response) {
          resolve(response)
        } else {
          reject(new Error('Passwords do not match.'))
        }
    })
  )
}

const updateUserToken = (token, user) => {
  return database.raw("UPDATE users SET token = ? WHERE id = ? RETURNING id, username, token", [token, user.id])
    .then((data) => data.rows[0])
}
```

### Pause and Digest

We've gotten a lot done, but we're not quite finished. Let's go back over what we have done so we can see clearer what's left to do.

We've gotten `/signup` and `/signin` working. 

`/signup` can:
  - create new users
  - securely encrypt users' passwords
  - generate a user token to be stored client-side
  - respond with a status of 201 and important user info
  
`/signin` can:
  - verify that a username and password in a request match a record in the database
  - regenerate a user's token to restore client-side
  - respond with a status of 200 and important user info
  
So what else do we need?
 
Well, if we have routes that need to be protected by authentication, we'd need to build in that functionality. 
 
Right now, we're passing a token back to our client that we're expecting the client to store for the duration of the user's session. 

For any routes that should be protected to authenticated users, we'd have to get that token back from the client and ensure that it matches the user's token within the database.

## Protecting Routes with Token Authentication

There are many, many ways we could go about this, but let's start with the most simple and straightforward.

We'll need to assume our client knows to send us the token we sent back on sign in with every authenticated request coming into our API.

That being said, we can create an `authenticate` function that takes the client's request body as an argument. We can use this as a helper function to conditionally return out of a different function should the request coming in not be from an authenticated user.

Our `authenticate` function can look something like this:

```js
// app/models/user.js
const authenticate = (userReq) => {
  findByToken(userReq.token)
    .then((user) => {
      if (user.username == userReq.username) {
        return true
      } else {
        return false
      }
    })
}

const findByToken = (token) => {
  return database.raw("SELECT * FROM users WHERE token = ?", [token])
    .then((data) => data.rows[0])
}
```

With that in place, imagine we have a route handled by a function called `userPhotos`. This function should be protected to only be accessed by authenticated users.

We could implement our `authorize` function like this:

```js
const userPhotos = (request, response) => {
  const userReq = request.body
  if (authenticate(userReq) {
      // handler logic goes here
   } else {
      response.status(404)
   }
}
```

That's the basis of authentication with an Express API! The rest is up to you to implement and customize.

## Extensions Worth Implementing

- ensure unique usernames on signup
- have requirements for length of password
- destroy the user's token on signout (both from DB and in client-side storage)
- refactor authorization function to its own class
- leverage Express middleware to handle authorization on protected routes
