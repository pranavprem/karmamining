import React from "react";

import TicketLayout from "./TicketLayout"
import Header from "../components/Header.js"
import Footer from "../components/Footer.js"


export default class Layout extends React.Component{
	constructor(){
    super();
    this.state = {
        "current":"unset"
        };
    
    }

    getcurrent(){
        return this.state.current;
    }

    setcurrent(curr){
        this.setState({"current":curr})
    }
    
	render() {
    
    return (
      <div>
          <Header />

            <TicketLayout getcurrent={this.getcurrent.bind(this)} setcurrent={this.setcurrent.bind(this)}/>
          <Footer />

      </div>


    );
  }



}