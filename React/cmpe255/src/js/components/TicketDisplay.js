import React from "react";


//import CalcElement from "./Calculator/CalcElement"

export default class TicketDisplay extends React.Component{


  
	render() {
   
    return (
      
       
          <tr style = {{paddingTop: 20 + "px", paddingBottom: 20 +"px", textAlign: "left", border: 20+"px solid #000"}}>
            <td colspan='5' style={{border: 20 + "px solid #fff", padding: 20 +"px", textAlign:"center", borderRadius:5}}>
              {this.props.comment.comment}
              </td>
            <td style={{border: 20 + "px solid #fff", padding: 20 +"px", textAlign:"center", borderRadius:5}}>
              {this.props.comment.score}
            </td>
          </tr>



    );
  }



}