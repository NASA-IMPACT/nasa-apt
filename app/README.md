
## nasa-apt App
Front end application for nasa-apt.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

`yarn install`

Installs necessary dependencies.

## Available Scripts

In the project directory, you can run:

`yarn start`

Runs the app in the development mode.<br>
Open [http://localhost:3006](http://localhost:3006) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.

`yarn test`

Runs the tap based unit tests.

`yarn run build`

Builds the app for production to the `build` folder.<br>
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br>
Your app is ready to be deployed!

The following environment variables are required.  You can copy and rename `.env.sample` to `.env` for use as a template.<br>
`PORT=3006`<br>
`SKIP_PREFLIGHT_CHECK=true`<br>
`REACT_APP_API_URL` The URL with port of the stac compliant api.<br>

### Design Approach

The application uses [Redux](https://redux.js.org/) for state management.

The application design uses both Presentational and Container components but makes liberal use of [react-redux](https://react-redux.js.org/docs/introduction/basic-tutorial) `connect` as outlined [here](https://redux.js.org/faq/reactredux#should-i-only-connect-my-top-component-or-can-i-connect-multiple-components-in-my-tree).

State that is transient or does not affect other components in the application can be maintained directly in components where appropriate as described [here](https://redux.js.org/faq/organizingstate#do-i-have-to-put-all-my-state-into-redux-should-i-ever-use-reacts-setstate).

Pure stateless React [components](https://reactjs.org/docs/state-and-lifecycle.html) are preferred but Class components are used where local state is required.

Any impure actions which may have side effects (asynchronous API requests, interaction with browser local storage) are isolated in Redux [middleware](https://redux.js.org/advanced/middleware).

Cross-cutting actions are also managed through the use of middleware.

The application store is configured to support the [redux-devtools-extension](https://github.com/zalmoxisus/redux-devtools-extension) for advanced debugging with state rewind and fast forward.

Because the application makes extensive use of [HOCs](https://reactjs.org/docs/higher-order-components.html), wrapped components are exposed as the default export while raw components are available as a named component.  This allows for unit testing without invoking HOC behavior.

The application uses [tape-await](https://github.com/mbostock/tape-await) to simplify asynchronous test flow for middleware.
