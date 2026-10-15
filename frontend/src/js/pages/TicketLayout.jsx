import { useRef, useState } from "react";
import { fetchScores } from "../../api.js";
import TicketDisplay from "../components/TicketDisplay.jsx";

export default function TicketLayout() {
  const [postId, setPostId] = useState("");
  const [submittedId, setSubmittedId] = useState("");
  const [comments, setComments] = useState(null);
  const [status, setStatus] = useState("Hit me with your Post ID");
  const [loading, setLoading] = useState(false);
  const requestId = useRef(0);

  function load(id) {
    const trimmed = id.trim();
    if (!trimmed) {
      setStatus("Enter a Reddit post ID first.");
      return;
    }
    const current = ++requestId.current;
    setSubmittedId(trimmed);
    setComments(null);
    setLoading(true);
    setStatus("Winter is coming. So are your results.");
    fetchScores(trimmed)
      .then((rows) => {
        if (current !== requestId.current) {
          return;
        }
        setComments(rows);
        setStatus(rows.length ? "There you go" : "That post has no comments.");
      })
      .catch((error) => {
        if (current !== requestId.current) {
          return;
        }
        setComments(null);
        setStatus(error.message);
      })
      .finally(() => {
        if (current === requestId.current) {
          setLoading(false);
        }
      });
  }

  const heading =
    submittedId === "demo"
      ? "Sample comments"
      : submittedId
        ? `Comments for post id ${submittedId}`
        : "Comments";

  return (
    <div className="container">
      <form
        className="controls"
        onSubmit={(event) => {
          event.preventDefault();
          load(postId);
        }}
      >
        <label htmlFor="post-id">Reddit post ID</label>
        <input
          id="post-id"
          className="form-control"
          placeholder="The id after /comments/ in a Reddit URL"
          type="text"
          value={postId}
          onChange={(event) => setPostId(event.target.value)}
        />
        <button className="btn btn-primary" type="submit" disabled={loading}>
          Show Me What you Got
        </button>
        <button
          className="btn btn-default"
          type="button"
          disabled={loading}
          onClick={() => load("demo")}
        >
          Try sample comments
        </button>
      </form>
      <h2>{heading}</h2>
      <p className="status" role="status">
        {status}
      </p>
      <table className="results">
        <thead>
          <tr>
            <th>Comment</th>
            <th className="score">Score</th>
          </tr>
        </thead>
        <tbody>
          {comments &&
            comments.map((comment) => (
              <TicketDisplay
                key={`${comment.score}-${comment.comment}`}
                comment={comment}
              />
            ))}
        </tbody>
      </table>
    </div>
  );
}
