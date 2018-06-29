import React from "react";
import ReactDOM from "react-dom";
import { Router, Route, IndexRoute, hashHistory } from "react-router";

import TicketLayout from "./pages/TicketLayout.js"


const app = document.getElementById('app');

ReactDOM.render(
    <Router history={hashHistory}>
      <Route path="/" component={TicketLayout}>
      </Route>
    </Router>,
  app);
