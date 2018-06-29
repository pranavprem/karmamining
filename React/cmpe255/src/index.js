import React from "react";
import ReactDOM from "react-dom";
//import { Router, Route, IndexRoute, hashHistory } from "react-router";


import { BrowserRouter as Router, Route } from 'react-router-dom';
import Layout from "./js/pages/OneRingToRuleThemAll";
import "./index.css"
ReactDOM.render(

    <Router>
    <div>
      <Route exact path ="/" component={Layout}/>
     </div> 
    </Router>,
   document.getElementById('root'));
