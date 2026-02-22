rsync -avz --progress --exclude '.DS_Store' * boscoh@149.28.166.13:modeldrop
ssh -t boscoh@149.28.166.13 "./modeldrop/reload.sh"
