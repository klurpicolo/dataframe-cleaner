import React from "react";
import { Route, Routes } from "react-router-dom";

import About from "../pages/About";
import DataframeCleanerPage from "../pages/DataframeCleanerPage";
import DataframeV1 from "../pages/DataframeV1";
import DataframeV2 from "../pages/DataframeV2";
import Home from "../pages/Home";

import { ROUTES } from "./RouterConfig";

const RouteWithRole = ({ Element }) => {
  return <Element />;
};

const Router = () => {
  return (
    <div>
      <Routes>
        <Route
          element={<RouteWithRole Element={Home} />}
          exact
          path={ROUTES.Home}
        />
        <Route
          element={<RouteWithRole Element={About} />}
          exact
          path={ROUTES.About}
        />
        <Route
          element={<RouteWithRole Element={DataframeV1} />}
          exact
          path={ROUTES.DataframeV1}
        />
        <Route
          element={<RouteWithRole Element={DataframeV2} />}
          exact
          path={ROUTES.DataframeV2}
        />
        <Route
          element={<RouteWithRole Element={DataframeCleanerPage} />}
          exact
          path={ROUTES.DataframeCleanerPage}
        />
      </Routes>
    </div>
  );
};

export default Router;
