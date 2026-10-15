export default function TicketDisplay({ comment }) {
  return (
    <tr>
      <td className="comment">{comment.comment}</td>
      <td className="score">{comment.score}</td>
    </tr>
  );
}
