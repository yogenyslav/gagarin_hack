import { Navigate } from 'react-router-dom';

type Props = {
    isSignedIn: boolean;
    children: React.ReactNode;
};

function ProtectedRoute({ isSignedIn, children }: Props): JSX.Element {
    if (!isSignedIn) {
        return <Navigate to='/login' replace />;
    }
    return children as JSX.Element;
}

export default ProtectedRoute;
