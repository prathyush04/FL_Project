# Frontend Application

This directory contains the user interface for the Federated Learning project. It is built as a Single Page Application (SPA) using **React 19** and **Vite**.

## Technologies Used
- **React 19**: Core UI library.
- **Vite**: Next-generation frontend tooling for fast development and building.
- **Tailwind CSS 4**: Utility-first CSS framework for rapid and responsive styling.
- **React Router (v7)**: Declarative routing for React applications.
- **Recharts**: Composable charting library built on React components for data visualization.
- **Axios**: Promise-based HTTP client for making API requests to the Spring Backend.
- **Lucide React**: Beautiful and consistent icons.

## Setup & Running

1. **Prerequisites:** Ensure you have Node.js and npm installed.

2. **Install dependencies:**
   Navigate to the `frontend` directory and run:
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   The application will start, and Vite will provide a local URL (typically `http://localhost:5173`) where you can view the application in your browser.

4. **Build for production:**
   ```bash
   npm run build
   ```
   This will create a `dist` directory with optimized, static assets ready for deployment.

5. **Linting:**
   ```bash
   npm run lint
   ```
   Uses `oxlint` to check for code quality issues.
