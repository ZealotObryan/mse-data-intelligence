"use client";

import { useMemo, useState } from "react";
import styles from "./InvestorAssessment.module.css";

const questions = [
 {q:"A company reports revenue of MWK 1,000,000 and net income of MWK 100,000. What is its net profit margin?",options:["1%","10%","100%"],answer:1,why:"Net profit margin = net income ÷ revenue = 100,000 ÷ 1,000,000 = 10%."},
 {q:"What does an ex-dividend date help an investor determine?",options:["When a share was first listed","Whether a share purchase qualifies for an announced dividend","The company's annual revenue"],answer:1,why:"The ex-dividend date is a key eligibility date. Investors should always check the official announcement and applicable market rules."},
 {q:"What happens when a buyer's bid price is below a seller's ask price?",options:["A trade must happen immediately","The order book can show an unmatched spread","The share price is guaranteed to rise"],answer:1,why:"If the best bid is below the best ask, there is a spread and the orders do not automatically match."},
 {q:"Why should financial ratios be compared across compatible reporting periods?",options:["To avoid misleading comparisons","To guarantee future returns","To remove all investment risk"],answer:0,why:"Different period lengths, currencies or accounting bases can make comparisons misleading."},
 {q:"Does diversification eliminate investment risk?",options:["Yes, completely","Only for large portfolios","No, it can reduce concentration but cannot remove all risk"],answer:2,why:"Diversification can reduce exposure to a single holding, but market-wide and other risks remain."}
];
export default function InvestorAssessment(){
 const [answers,setAnswers]=useState<Record<number,number>>({});
 const [submitted,setSubmitted]=useState(false);
 const score=useMemo(()=>questions.reduce((n,q,i)=>n+(answers[i]===q.answer?1:0),0),[answers]);
 const complete=Object.keys(answers).length===questions.length;
 return <section className={styles.card} aria-labelledby="assessment-title">
  <div className={styles.heading}><div><span className={styles.kicker}>KNOWLEDGE CHECK · ASSESSMENT 08</span><h2 id="assessment-title">Test your investor knowledge</h2><p>Apply what you have explored. Choose an answer for each question, then review the explanations.</p></div><span className={styles.tag}>5 QUESTIONS</span></div>
  <div className={styles.progress}><span style={{width:(Object.keys(answers).length/questions.length*100)+"%"}}/></div>
  {questions.map((q,i)=><fieldset className={styles.question} key={q.q} disabled={submitted}><legend><b>{String(i+1).padStart(2,"0")}</b>{q.q}</legend><div className={styles.options}>{q.options.map((option,j)=><label key={option} className={answers[i]===j?styles.selected:""}><input type="radio" name={"question-"+i} checked={answers[i]===j} onChange={()=>setAnswers(current=>({...current,[i]:j}))}/>{option}</label>)}</div>{submitted&&<div className={styles.feedback}><b>{answers[i]===q.answer?"Correct":"Review this concept"}</b><p>{q.why}</p></div>}</fieldset>)}
  {!submitted?<button className={styles.submit} type="button" disabled={!complete} onClick={()=>setSubmitted(true)}>Submit answers</button>:<div className={styles.result} aria-live="polite"><strong>{score} / {questions.length}</strong><p>{score===questions.length?"Excellent work. You have answered every question correctly.":score>=3?"Good progress. Review the explanations for the questions you missed.":"Keep learning. Revisit the Practice Lab tools and try again."}</p><button type="button" onClick={()=>{setAnswers({});setSubmitted(false)}}>Try again</button></div>}
  <p className={styles.disclosure}>This short knowledge check is educational and does not represent a regulated investor competency test. Your answers are held only in this page session and are not saved to an account.</p>
 </section>;
}
