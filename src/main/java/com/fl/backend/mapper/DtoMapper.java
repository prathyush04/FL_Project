package com.fl.backend.mapper;

import com.fl.backend.dto.*;
import com.fl.backend.entity.*;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface DtoMapper {

    HospitalDto toHospitalDto(Hospital hospital);

    TrainingSessionDto toTrainingSessionDto(TrainingSession session);

    @Mapping(source = "session.id", target = "sessionId")
    FederatedRoundDto toFederatedRoundDto(FederatedRound round);

    @Mapping(source = "round.id", target = "roundId")
    @Mapping(source = "hospital.id", target = "hospitalId")
    ClientRoundStatusDto toClientRoundStatusDto(ClientRoundStatus status);

    @Mapping(source = "session.id", target = "sessionId")
    ModelVersionDto toModelVersionDto(ModelVersion modelVersion);

    @Mapping(source = "hospital.id", target = "hospitalId")
    @Mapping(source = "modelVersion.id", target = "modelVersionId")
    PredictionDto toPredictionDto(Prediction prediction);

    @Mapping(source = "session.id", target = "sessionId")
    ComparisonResultDto toComparisonResultDto(ComparisonResult result);
}
