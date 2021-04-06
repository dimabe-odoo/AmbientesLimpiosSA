from datetime import date

def add_zeros(init, to):
    return ''.join(['0' for i in range(init, to)])

def reset_series(now):
    return add_zeros(1, 5) + '1-' + now.strftime('%y%m%d')


def generate_lot(currentLot = None):
    now = date.today() 

    if currentLot is None:
        return reset_series(now)

    if currentLot:
        lots = currentLot.split('-')
        year = lots[1]
        if year[0:2] != now.strftime('%y'):
            return reset_series(now)

        sequence = lots[0]
        sequence = int(sequence) + 1
        max_lenght = len(str(sequence)) + 1 if len(str(sequence)) > 5 else 5;

        next_lot = add_zeros(len(str(sequence)), max_lenght)

        next_lot += '{}-{}'.format(str(sequence), now.strftime('%y%m%d')) 

        return next_lot 