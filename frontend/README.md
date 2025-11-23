# Jude Presentation Frontend

This is the React-based presentation interface for the Jude project.

## 🚀 How to Start

1.  Open a terminal in the `frontend` directory:
    ```bash
    cd frontend
    ```

2.  Start the development server:
    ```bash
    npm run dev
    ```

3.  Open your browser at the URL shown (usually `http://localhost:5173`).

## 🛠 Customization

### Evaluation Data
To update the charts in the Dashboard, edit `src/components/presentation/Dashboard.tsx`:
Look for `const evaluationData = [...]`.

### Team Members
To update the team section, edit `src/components/presentation/Dashboard.tsx` inside the `activeTab === 'team'` section.

### API Integration
The `DemoInterface.tsx` is currently in **Simulation Mode**.
To connect it to the real backend:
1.  Uncomment the API call logic in `handleSubmit`.
2.  Ensure the backend is running on port 5555.

## 🎨 Key Features
- **3D Scroll Navigation**: Implemented in `ScrollSection.tsx`.
- **Interactive Dashboard**: Overlay for academic data presentation.
- **Live Demo UI**: Ready for multimodal interaction.
