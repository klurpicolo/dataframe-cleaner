import * as Sentry from "@sentry/react";
import React from "react";
import { Provider } from "react-redux";
import DataFrameDisplay from "./pages/DataFrameDisplay";
import Home from "./pages/Home";
import configureStore from "./store";

import { BrowserRouter } from 'react-router-dom';
import Router from './routes/Router';
import Example from "./component/Example";

const store = configureStore({});
const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <Provider store={store}>
      {/* <DataFrameDisplay/> */}
      {/* <Example/> */}
      {/* <Home /> */}
      <BrowserRouter>
        <Router/>
      </BrowserRouter>
    </Provider>
  </Sentry.ErrorBoundary>
);

export default App;
