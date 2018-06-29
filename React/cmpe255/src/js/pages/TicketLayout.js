import React from "react";

import TicketDisplay from "../components/TicketDisplay.js"

export default class TicketLayout extends React.Component {
  constructor(){
    super();
    this.state = {"comments":null, "isloading":"Hit me with your Post ID"};
    //const client = require('./Restclient');
   
  }

  componentDidMount() {
    console.log("it did this");
    
    if (this.props.getcurrent()!=="unset"){
      this.setState({"isloading":"Winter is coming. So are your results."})
      var url = "http://0.0.0.0:8080/combined/"+this.props.getcurrent();
      console.log(url);
      fetch(url, 
            {
              method: 'GET',
              headers: {
                  'Content-Type': 'application/json'
              }
            })
      .then(result => result.json())
      .then(item => this.setState({"isloading":"There you go", "comments":item}));
      console.log(this.state.comments);
    }
  }

  register(){
      this.props.setcurrent(document.getElementById("username").value);
      console.log("it did this");
      this.setState({"isloading":"Winter is coming. So are your results."})
      if (this.props.getcurrent!=="unset"){
        var url = "http://0.0.0.0:8080/combined/"+document.getElementById("username").value;
        console.log(url);
        fetch(url, 
              {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
              })
        .then(result => result.json())
        .then(item => this.setState({"isloading":"There you go", "comments":item}));
        console.log(this.state.comments);
      }


    }

  
  
  render() {
    // setTimeout(()=>{
    //   this.setState({name:"Pranav2"});
    // },2000);
    return (
      <div className="container">
      
        <center><input placeholder="Enter Comment ID" type="text" id="username"/><br/><br/>
        <button class="btn" onClick={()=>{this.register()}}>Show Me What you Got</button><br/>
        <h1> Comments for post id {this.props.getcurrent()} </h1>
        {this.state.isloading}</center>
        
        <table style={{borderCollapse: "collapse", width: 100+"%", borderRadius: 10+"px"}}>
         <tbody>
          {this.state && this.state.comments  && this.state.comments.map(comment => <TicketDisplay comment={comment} />)}
                  </tbody>
      </table>
      </div>    
    );
  }
}
