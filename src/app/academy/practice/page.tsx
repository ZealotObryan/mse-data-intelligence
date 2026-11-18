import Link from "next/link";
import InvestmentReturnSimulator from "@/components/academy/InvestmentReturnSimulator";
import DividendCalculator from "@/components/academy/DividendCalculator";
import OrderBookSimulator from "@/components/academy/OrderBookSimulator";
import MarketFlowExplorer from "@/components/academy/MarketFlowExplorer";
import PortfolioBuilder from "@/components/academy/PortfolioBuilder";
import RiskReturnExplorer from "@/components/academy/RiskReturnExplorer";
import FinancialRatioPlayground from "@/components/academy/FinancialRatioPlayground";
import InvestorAssessment from "@/components/academy/InvestorAssessment";
import styles from "./page.module.css";

export const metadata = {
  title: "Investor Academy Practice Lab | MSE Analytics",
  description: "Interactive, illustrative financial learning tools for the MSE Investor Academy."
};

export default function AcademyPracticePage() {
  return (
    <main className={styles.page}>
      <header className={styles.top}>
        <Link href="/" className={styles.back}>← Back to MSE Data Intelligence</Link>
        <span>MALAWI STOCK EXCHANGE · INVESTOR ACADEMY</span>
      </header>
      <section className={styles.hero}>
        <span className={styles.kicker}>PRACTICE LAB</span>
        <h1>Learn by exploring.</h1>
        <p>Change the assumptions, see what happens, and understand the calculations behind common investment concepts.</p>
        <div className={styles.disclosure}>Educational simulations only · No live MSE prices or company data are used.</div>
      </section>
      <nav aria-label="Practice Lab sections" className={styles.toolsNav}>
        <a href="#market-mechanics">Market mechanics</a>
        <a href="#portfolio-tools">Portfolio tools</a>
        <a href="#financial-analysis">Financial analysis</a>
        <a href="#knowledge-check">Knowledge check</a>
      </nav>
      <div className={styles.tools}>
        <section id="market-mechanics" aria-label="Market mechanics tools" className={styles.toolGroup}>
          <InvestmentReturnSimulator />
          <DividendCalculator />
          <OrderBookSimulator />
          <MarketFlowExplorer />
        </section>
        <section id="portfolio-tools" aria-label="Portfolio tools" className={styles.toolGroup}>
          <PortfolioBuilder />
          <RiskReturnExplorer />
        </section>
        <section id="financial-analysis" aria-label="Financial analysis tools" className={styles.toolGroup}>
          <FinancialRatioPlayground />
        </section>
        <section id="knowledge-check" aria-label="Investor knowledge assessment" className={styles.toolGroup}>
          <InvestorAssessment />
        </section>
      </div>
      <footer className={styles.footer}>All values are hypothetical. These tools are for financial education, not investment advice. Actual investment outcomes may differ and may include fees, taxes and other costs.</footer>
    </main>
  );
}
