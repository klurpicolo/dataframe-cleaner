import React from "react";
import { Route, Routes } from "react-router-dom";

import About from "../pages/About";
import DataframeV1 from "../pages/DataframeV1";
import DataframeV2 from "../pages/DataframeV2";
import DataframeV3 from "../pages/DataframeV3";
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
          element={<RouteWithRole Element={DataframeV3} />}
          exact
          path={ROUTES.DataframeV3}
        />
      </Routes>
    </div>
  );
};

export default Router;
