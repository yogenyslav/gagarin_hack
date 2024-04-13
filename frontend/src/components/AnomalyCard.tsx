import { Anomaly } from '../api/models';

type Props = {
    anomaly: Anomaly;
};

const AnomalyCard = ({ anomaly }: Props) => {
    return (
        <div>
            <img style={{ width: '100%' }} src={anomaly.link} alt='anomaly' />
        </div>
    );
};

export default AnomalyCard;
